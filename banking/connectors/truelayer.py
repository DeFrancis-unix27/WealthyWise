from typing import Optional
import requests
from .base import BankConnector, BankAccountInfo, TransactionData


class TruelayerConnector(BankConnector):
    provider = "truelayer"

    def _get_config(self):
        from banking.models import BankConnectorConfig
        try:
            return BankConnectorConfig.objects.get(provider="truelayer", is_active=True)
        except BankConnectorConfig.DoesNotExist:
            raise RuntimeError(
                "Truelayer connector not configured. Add a BankConnectorConfig with provider='truelayer'."
            )

    def _auth_header(self, access_token: str) -> dict:
        return {"Authorization": f"Bearer {access_token}"}

    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        config = self._get_config()
        env_prefix = "auth" if config.environment == "production" else "sandbox-auth"
        return (
            f"https://{env_prefix}.truelayer.com/connect/?"
            f"response_type=code&client_id={config.client_id}&"
            f"scope=info%20accounts%20transactions%20offline_access&"
            f"redirect_uri={redirect_uri}&state={state}&providers=uk-ob-all%20uk-ca-all%20uk-oc-all"
        )

    def exchange_token(self, code: str, redirect_uri: str) -> str:
        config = self._get_config()
        env_prefix = "auth" if config.environment == "production" else "sandbox-auth"
        resp = requests.post(
            f"https://{env_prefix}.truelayer.com/connect/token",
            data={
                "grant_type": "authorization_code",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def get_accounts(self, access_token: str) -> list[BankAccountInfo]:
        resp = requests.get(
            "https://api.truelayer.com/data/v1/accounts",
            headers=self._auth_header(access_token),
            timeout=30,
        )
        resp.raise_for_status()
        accounts = []
        for acct in resp.json().get("results", []):
            accounts.append(
                BankAccountInfo(
                    account_id=acct["account_id"],
                    account_number=acct.get("account_number", {}).get("number", ""),
                    account_name=acct.get("display_name", ""),
                    institution_name=acct.get("provider", {}).get("display_name", ""),
                    institution_id=acct.get("provider", {}).get("provider_id", ""),
                    currency=acct.get("currency", "GBP"),
                    balance=acct.get("balance", {}).get("current", 0),
                )
            )
        return accounts

    def get_transactions(
        self, access_token: str, account_id: str, cursor: Optional[str] = None
    ) -> tuple[list[TransactionData], Optional[str]]:
        params = {}
        if cursor:
            params["from"] = cursor
        resp = requests.get(
            f"https://api.truelayer.com/data/v1/accounts/{account_id}/transactions",
            headers=self._auth_header(access_token),
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        transactions = []
        for tx in data.get("results", []):
            transactions.append(
                TransactionData(
                    transaction_id=tx["transaction_id"],
                    amount=tx["amount"],
                    currency=tx.get("currency", "GBP"),
                    description=tx.get("description", ""),
                    category=None,
                    date=tx["timestamp"][:10],
                    type="debit" if tx.get("debit") else "credit",
                )
            )
        return transactions, data.get("next_cursor")

    def revoke_token(self, access_token: str) -> bool:
        return True
