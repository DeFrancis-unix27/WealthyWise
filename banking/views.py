import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import LinkedBank, SyncLog, BankConnectorConfig
from .connectors import get_connector, CONNECTOR_MAP


@login_required
def bank_list_view(request):
    linked_banks = LinkedBank.objects.filter(user=request.user)
    providers = BankConnectorConfig.objects.filter(is_active=True)
    return render(request, "banking/bank_list.html", {
        "linked_banks": linked_banks,
        "providers": providers,
    })


@login_required
@require_GET
def link_bank_view(request, provider: str):
    if provider not in CONNECTOR_MAP:
        messages.error(request, f"Unknown provider: {provider}")
        return redirect("bank_list")

    try:
        connector = get_connector(provider)
    except RuntimeError as e:
        messages.error(request, str(e))
        return redirect("bank_list")

    state = str(uuid.uuid4())
    request.session["bank_link_state"] = state
    request.session["bank_link_provider"] = provider

    redirect_uri = request.build_absolute_uri("/banking/callback/")
    auth_url = connector.get_auth_url(redirect_uri, state)

    return redirect(auth_url)


@login_required
def bank_callback_view(request):
    saved_state = request.session.pop("bank_link_state", None)
    provider = request.session.pop("bank_link_provider", None)
    code = request.GET.get("code")
    state = request.GET.get("state")
    error = request.GET.get("error")

    if error:
        messages.error(request, f"Bank link canceled: {error}")
        return redirect("bank_list")

    if not code or not provider:
        messages.error(request, "Invalid bank link response.")
        return redirect("bank_list")

    if state and saved_state and state != saved_state:
        messages.error(request, "Security check failed. Please try again.")
        return redirect("bank_list")

    try:
        connector = get_connector(provider)
        redirect_uri = request.build_absolute_uri("/banking/callback/")
        access_token = connector.exchange_token(code, redirect_uri)
        accounts = connector.get_accounts(access_token)
    except Exception as e:
        messages.error(request, f"Failed to link bank: {e}")
        return redirect("bank_list")

    for acct in accounts:
        LinkedBank.objects.create(
            user=request.user,
            provider=provider,
            access_token=access_token,
            reference=acct.account_id,
            institution_name=acct.institution_name,
            institution_id=acct.institution_id,
            account_id=acct.account_id,
            account_number=acct.account_number[:50],
            account_name=acct.account_name,
            currency=acct.currency,
        )

    messages.success(request, f"Bank linked successfully! {len(accounts)} account(s) found.")
    return redirect("bank_list")


@login_required
@require_POST
def unlink_bank_view(request, bank_id: int):
    linked_bank = get_object_or_404(LinkedBank, id=bank_id, user=request.user)

    try:
        connector = get_connector(linked_bank.provider)
        connector.revoke_token(linked_bank.access_token)
    except Exception:
        pass

    linked_bank.status = "revoked"
    linked_bank.save(update_fields=["status"])
    messages.success(request, f"{linked_bank.institution_name} unlinked.")
    return redirect("bank_list")


@login_required
@require_POST
def sync_bank_view(request, bank_id: int):
    linked_bank = get_object_or_404(LinkedBank, id=bank_id, user=request.user)
    sync_log = SyncLog.objects.create(
        linked_bank=linked_bank,
        status="running",
        started_at=timezone.now(),
    )

    try:
        connector = get_connector(linked_bank.provider)
        accounts = connector.get_accounts(linked_bank.access_token)
        total_created = 0

        for account_info in accounts:
            from financeapp.models import Account, Transaction

            django_account, _ = Account.objects.get_or_create(
                user=request.user,
                name=f"{linked_bank.institution_name} - {account_info.account_name}",
                defaults={
                    "account_type": "Bank",
                    "account_number": account_info.account_number[:20],
                    "currency": account_info.currency,
                    "balance": account_info.balance,
                },
            )

            cursor = None
            tx_found = 0
            tx_created = 0
            tx_skipped = 0

            while True:
                transactions, cursor = connector.get_transactions(
                    linked_bank.access_token,
                    account_info.account_id,
                    cursor=cursor,
                )
                tx_found += len(transactions)

                for tx_data in transactions:
                    exists = Transaction.objects.filter(
                        user=request.user,
                        account=django_account,
                        description=tx_data.description[:255],
                        amount=tx_data.amount,
                        date=tx_data.date,
                    ).exists()

                    if exists:
                        tx_skipped += 1
                        continue

                    Transaction.objects.create(
                        user=request.user,
                        account=django_account,
                        transaction_type="income" if tx_data.type == "credit" else "expense",
                        amount=tx_data.amount,
                        description=tx_data.description[:255],
                        category=tx_data.category or "other",
                        date=tx_data.date,
                    )
                    tx_created += 1
                    total_created += 1

                if not cursor:
                    break

            sync_log.transactions_found = tx_found
            sync_log.transactions_created = tx_created
            sync_log.transactions_skipped = tx_skipped

        linked_bank.last_sync_at = timezone.now()
        linked_bank.save(update_fields=["last_sync_at"])
        sync_log.status = "success"
        sync_log.completed_at = timezone.now()
        sync_log.save()

        return JsonResponse({
            "status": "success",
            "created": total_created,
        })

    except Exception as e:
        sync_log.status = "failed"
        sync_log.error_message = str(e)
        sync_log.completed_at = timezone.now()
        sync_log.save()
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def webhook_view(request, provider: str):
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    try:
        connector = get_connector(provider)
    except (ValueError, RuntimeError):
        return HttpResponse(status=400)

    account_id = payload.get("account_id") or payload.get("data", {}).get("account", {}).get("_id")

    if account_id:
        linked_banks = LinkedBank.objects.filter(
            account_id=account_id, provider=provider, status="active"
        )
        for bank in linked_banks:
            try:
                accounts = connector.get_accounts(bank.access_token)
                for acct in accounts:
                    transactions, _ = connector.get_transactions(
                        bank.access_token, acct.account_id
                    )
                    for tx in transactions:
                        from financeapp.models import Transaction, Account
                        if not Transaction.objects.filter(
                            user=bank.user, description=tx.description[:255],
                            amount=tx.amount, date=tx.date,
                        ).exists():
                            Transaction.objects.create(
                                user=bank.user,
                                account=Account.objects.filter(user=bank.user).first(),
                                transaction_type="income" if tx.type == "credit" else "expense",
                                amount=tx.amount,
                                description=tx.description[:255],
                                date=tx.date,
                            )
            except Exception:
                pass

    return HttpResponse(status=200)
