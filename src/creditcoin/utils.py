import hashlib
from typing import Any, Dict
import secrets

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

def validate_mnemonic(mnemonic: str) -> bool:
    """
    Basic mnemonic validation
    
    Args:
        mnemonic: Mnemonic phrase to validate
        
    Returns:
        True if mnemonic appears valid
    """
    words = mnemonic.strip().split()
    return len(words) in [12, 15, 18, 21, 24] and all(len(word) >= 3 for word in words)

def generate_random_entropy(bits: int = 128) -> bytes:
    """
    Generate cryptographically secure random entropy
    
    Args:
        bits: Number of bits (128, 160, 192, 224, 256)
        
    Returns:
        Random bytes
    """
    if bits not in [128, 160, 192, 224, 256]:
        raise ValueError("Bits must be 128, 160, 192, 224, or 256")
    
    return secrets.token_bytes(bits // 8)