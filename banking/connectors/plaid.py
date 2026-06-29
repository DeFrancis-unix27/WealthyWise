from typing import Optional
import json
from .base import BankConnector, BankAccountInfo, TransactionData


class PlaidConnector(BankConnector):
    provider = "plaid"

    def _get_config(self):
        from banking.models import BankConnectorConfig
        try:
            return BankConnectorConfig.objects.get(provider="plaid", is_active=True)
        except BankConnectorConfig.DoesNotExist:
            raise RuntimeError(
                "Plaid connector not configured. Add a BankConnectorConfig with provider='plaid'."
            )

    def _env(self):
        config = self._get_config()
        return "sandbox" if config.environment == "sandbox" else "development" if config.environment == "development" else "production"

    def _api_url(self, path: str) -> str:
        env = self._env()
        return f"https://{env}.plaid.com/{path}"

    def _post(self, path: str, body: dict):
        import requests
        config = self._get_config()
        body["client_id"] = config.client_id
        body["secret"] = config.client_secret
        resp = requests.post(self._api_url(path), json=body, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        data = self._post("link/token/create", {
            "user": {"client_user_id": state},
            "client_name": "WealthPoint",
            "products": ["transactions"],
            "country_codes": ["US", "CA"],
            "language": "en",
            "redirect_uri": redirect_uri,
        })
        link_token = data["link_token"]
        env = self._env()
        return f"https://{env}.plaid.com/link?token={link_token}"

    def exchange_token(self, code: str, redirect_uri: str) -> str:
        data = self._post("item/public_token/exchange", {
            "public_token": code,
        })
        return data["access_token"]

    def get_accounts(self, access_token: str) -> list[BankAccountInfo]:
        data = self._post("accounts/get", {
            "access_token": access_token,
        })
        accounts = []
        for acct in data.get("accounts", []):
            accounts.append(
                BankAccountInfo(
                    account_id=acct["account_id"],
                    account_number=acct.get("mask", ""),
                    account_name=acct.get("name", ""),
                    institution_name=data.get("item", {}).get("institution_name", ""),
                    institution_id=data.get("item", {}).get("institution_id", ""),
                    currency=acct.get("balances", {}).get("iso_currency_code", "USD"),
                    balance=acct.get("balances", {}).get("current", 0),
                )
            )
        return accounts

    def get_transactions(
        self, access_token: str, account_id: str, cursor: Optional[str] = None
    ) -> tuple[list[TransactionData], Optional[str]]:
        body = {
            "access_token": access_token,
            "start_date": "2024-01-01",
            "end_date": "2030-12-31",
            "options": {"account_ids": [account_id]},
        }
        if cursor:
            body["options"]["cursor"] = cursor
        data = self._post("transactions/sync", body)
        transactions = []
        for tx in data.get("added", []):
            transactions.append(
                TransactionData(
                    transaction_id=tx["transaction_id"],
                    amount=tx["amount"],
                    currency="USD",
                    description=tx.get("name", ""),
                    category=tx.get("category", [None])[0] if tx.get("category") else None,
                    date=tx["date"],
                    type="debit" if tx["amount"] > 0 else "credit",
                )
            )
        return transactions, data.get("next_cursor")

    def revoke_token(self, access_token: str) -> bool:
        data = self._post("item/remove", {
            "access_token": access_token,
        })
        return data.get("removed", False)
