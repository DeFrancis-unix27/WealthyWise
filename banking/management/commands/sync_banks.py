from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from banking.models import LinkedBank, SyncLog
from banking.connectors import get_connector
from financeapp.models import Account, Transaction


class Command(BaseCommand):
    help = "Sync transactions for all active linked banks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id", type=int, help="Sync only for a specific user ID"
        )
        parser.add_argument(
            "--bank-id", type=int, help="Sync only for a specific linked bank ID"
        )

    def handle(self, *args, **options):
        queryset = LinkedBank.objects.filter(status="active")
        if options["user_id"]:
            queryset = queryset.filter(user_id=options["user_id"])
        if options["bank_id"]:
            queryset = queryset.filter(id=options["bank_id"])

        synced = 0
        failed = 0

        for linked_bank in queryset:
            sync_log = SyncLog.objects.create(
                linked_bank=linked_bank,
                status="running",
                started_at=timezone.now(),
            )
            try:
                connector = get_connector(linked_bank.provider)
                accounts = connector.get_accounts(linked_bank.access_token)

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
                synced += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Synced: {linked_bank} "
                        f"({sync_log.transactions_created} new, "
                        f"{sync_log.transactions_skipped} skipped)"
                    )
                )

            except Exception as e:
                sync_log.status = "failed"
                sync_log.error_message = str(e)
                sync_log.completed_at = timezone.now()
                sync_log.save()
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f"Failed: {linked_bank} - {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Done. Synced: {synced}, Failed: {failed}")
        )
