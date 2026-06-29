from typing import Optional
from django.conf import settings
from .base import BankConnector, BankAccountInfo, TransactionData


class MonoConnector(BankConnector):
    provider = "mono"

    def _get_config(self):
        from banking.models import BankConnectorConfig
        try:
            return BankConnectorConfig.objects.get(provider="mono", is_active=True)
        except BankConnectorConfig.DoesNotExist:
            raise RuntimeError(
                "Mono connector not configured. Add a BankConnectorConfig with provider='mono'."
            )

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        config = self._get_config()
        base = "https://api.withmono.com/oauth/authorize"
        return f"{base}?client_id={config.client_id}&redirect_uri={redirect_uri}&state={state}"

    def exchange_token(self, code: str, redirect_uri: str) -> str:
        import requests
        config = self._get_config()
        resp = requests.post(
            "https://api.withmono.com/oauth/token",
            json={"code": code, "client_id": config.client_id, "client_secret": config.client_secret},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def get_accounts(self, access_token: str) -> list[BankAccountInfo]:
        import requests
        resp = requests.get(
            "https://api.withmono.com/account",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            BankAccountInfo(
                account_id=data["account"]["_id"],
                account_number=data["account"].get("accountNumber", ""),
                account_name=data["account"].get("name", ""),
                institution_name=data["account"].get("institution", {}).get("name", ""),
                institution_id=data["account"].get("institution", {}).get("bankCode", ""),
                currency=data["account"].get("currency", "NGN"),
                balance=data["account"].get("balance", 0),
            )
        ]

    def get_transactions(
        self, access_token: str, account_id: str, cursor: Optional[str] = None
    ) -> tuple[list[TransactionData], Optional[str]]:
        import requests
        params = {}
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(
            f"https://api.withmono.com/accounts/{account_id}/transactions",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        transactions = []
        for tx in data.get("data", []):
            transactions.append(
                TransactionData(
                    transaction_id=tx["_id"],
                    amount=tx["amount"],
                    currency=tx.get("currency", "NGN"),
                    description=tx.get("narration", ""),
                    category=tx.get("category"),
                    date=tx["date"],
                    type="debit" if tx["type"] == "debit" else "credit",
                )
            )
        return transactions, data.get("next", {}).get("cursor")

    def revoke_token(self, access_token: str) -> bool:
        import requests
        config = self._get_config()
        resp = requests.post(
            "https://api.withmono.com/account/auth",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={"secret": config.client_secret},
            timeout=30,
        )
        return resp.status_code == 200
