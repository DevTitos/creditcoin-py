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