"""
Creditcoin SDK - A Python SDK for interacting with Creditcoin blockchain
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .client import CreditScanClient
from .models import (
    AddressInfo,
    Transaction,
    BlockInfo,
    NetworkStats,
    AskOrder,
    BidOrder,
    DealOrder
)
from .exceptions import (
    CreditScanError,
    NetworkError,
    InvalidAddressError,
    TransactionError
)

__all__ = [
    "CreditScanClient",
    "AddressInfo",
    "Transaction", 
    "BlockInfo",
    "NetworkStats",
    "AskOrder",
    "BidOrder",
    "DealOrder",
    "CreditScanError",
    "NetworkError",
    "InvalidAddressError",
    "TransactionError",
]