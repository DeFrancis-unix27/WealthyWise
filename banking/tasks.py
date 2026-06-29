from celery import shared_task
from django.utils import timezone
from .models import LinkedBank, SyncLog
from .connectors import get_connector
from financeapp.models import Account, Transaction


@shared_task(bind=True, max_retries=3)
def sync_linked_bank(self, linked_bank_id: int):
    try:
        linked_bank = LinkedBank.objects.get(id=linked_bank_id, status="active")
    except LinkedBank.DoesNotExist:
        return {"error": "Linked bank not found or inactive"}

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
            django_account, _ = Account.objects.get_or_create(
                user=linked_bank.user,
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
                        user=linked_bank.user,
                        account=django_account,
                        description=tx_data.description[:255],
                        amount=tx_data.amount,
                        date=tx_data.date,
                    ).exists()

                    if exists:
                        tx_skipped += 1
                        continue

                    Transaction.objects.create(
                        user=linked_bank.user,
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

        return {
            "status": "success",
            "created": total_created,
            "linked_bank_id": linked_bank_id,
        }

    except Exception as e:
        sync_log.status = "failed"
        sync_log.error_message = str(e)
        sync_log.completed_at = timezone.now()
        sync_log.save()

        try:
            self.retry(countdown=60 * 5)
        except Exception:
            pass

        return {"status": "error", "error": str(e), "linked_bank_id": linked_bank_id}
