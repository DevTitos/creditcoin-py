import hashlib
from typing import Any, Dict

def format_amount(amount: int, decimals: int = 18) -> float:
    """Convert raw amount to human readable format"""
    return amount / (10 ** decimals)

def to_raw_amount(amount: float, decimals: int = 18) -> int:
    """Convert human readable amount to raw amount"""
    return int(amount * (10 ** decimals))

def generate_hash(data: Dict[str, Any]) -> str:
    """Generate SHA256 hash for data"""
    data_str = str(sorted(data.items()))
    return hashlib.sha256(data_str.encode()).hexdigest()