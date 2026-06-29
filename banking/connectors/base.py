from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class BankAccountInfo:
    account_id: str
    account_number: str
    account_name: str
    institution_name: str
    institution_id: str
    currency: str
    balance: float


@dataclass
class TransactionData:
    transaction_id: str
    amount: float
    currency: str
    description: str
    category: Optional[str]
    date: str
    type: str  # "credit" or "debit"


class BankConnector(ABC):
    provider: str = ""

    @abstractmethod
    def get_auth_url(self, redirect_uri: str, state: str) -> str:
        pass

    @abstractmethod
    def exchange_token(self, code: str, redirect_uri: str) -> str:
        pass

    @abstractmethod
    def get_accounts(self, access_token: str) -> list[BankAccountInfo]:
        pass

    @abstractmethod
    def get_transactions(
        self, access_token: str, account_id: str, cursor: Optional[str] = None
    ) -> tuple[list[TransactionData], Optional[str]]:
        pass

    @abstractmethod
    def revoke_token(self, access_token: str) -> bool:
        pass
