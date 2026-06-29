from .base import BankConnector
from .mono import MonoConnector
from .plaid import PlaidConnector
from .truelayer import TruelayerConnector

CONNECTOR_MAP = {
    "mono": MonoConnector,
    "plaid": PlaidConnector,
    "truelayer": TruelayerConnector,
}


def get_connector(provider: str) -> BankConnector:
    cls = CONNECTOR_MAP.get(provider)
    if not cls:
        raise ValueError(f"Unknown provider: {provider}")
    return cls()
