class CreditScanError(Exception):
    """Base exception for Credit Scan SDK"""
    pass

class NetworkError(CreditScanError):
    """Network related errors"""
    pass

class InvalidAddressError(CreditScanError):
    """Invalid address format"""
    pass

class TransactionError(CreditScanError):
    """Transaction related errors"""
    pass

class ConfigurationError(CreditScanError):
    """Configuration related errors"""
    pass

class CreditScanError(Exception):
    """Base exception for Credit Scan SDK"""
    pass

class NetworkError(CreditScanError):
    """Network related errors"""
    pass

class InvalidAddressError(CreditScanError):
    """Invalid address format"""
    pass

class TransactionError(CreditScanError):
    """Transaction related errors"""
    pass

class ConfigurationError(CreditScanError):
    """Configuration related errors"""
    pass

class InsufficientBalanceError(CreditScanError):
    """Insufficient balance for transaction"""
    pass

class AccountError(CreditScanError):
    """Account related errors"""
    pass

class KeypairError(AccountError):
    """Keypair generation/management errors"""
    pass