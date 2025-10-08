import json
import logging
from typing import Optional, List, Dict, Any, Union
from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException
from scalecodec.base import ScaleBytes
from .credit_contracts import CreditContractManager
from .models import (
    AddressInfo,
    Transaction,
    BlockInfo,
    NetworkStats,
    AskOrder,
    BidOrder,
    DealOrder,
    Keypair as SDKKeypair,
    TransactionReceipt,
    TokenBalance
)
from .exceptions import (
    CreditScanError,
    NetworkError,
    InvalidAddressError,
    TransactionError,
    InsufficientBalanceError,
    KeypairError
)

logger = logging.getLogger(__name__)


class AccountManager:
    """
    Account management for Creditcoin
    Handles keypair generation, import/export, and signing
    """
    
    @staticmethod
    def generate_mnemonic(words_count: int = 12) -> str:
        """
        Generate a new mnemonic phrase
        
        Args:
            words_count: Number of words in mnemonic (12, 15, 18, 21, 24)
            
        Returns:
            Mnemonic phrase as string
        """
        if words_count not in [12, 15, 18, 21, 24]:
            raise KeypairError("Word count must be 12, 15, 18, 21, or 24")
        
        return Keypair.generate_mnemonic(words_count=words_count)
    
    @staticmethod
    def create_from_mnemonic(mnemonic: str, ss58_format: int = 42) -> SDKKeypair:
        """
        Create keypair from mnemonic phrase
        
        Args:
            mnemonic: Mnemonic phrase
            ss58_format: SS58 format for address encoding
            
        Returns:
            SDKKeypair object
        """
        try:
            keypair = Keypair.create_from_mnemonic(
                mnemonic, 
                ss58_format=ss58_format
            )
            
            return SDKKeypair(
                mnemonic=mnemonic,
                private_key=keypair.private_key,
                public_key=keypair.public_key,
                address=keypair.ss58_address,
                ss58_format=ss58_format
            )
        except Exception as e:
            raise KeypairError(f"Failed to create keypair from mnemonic: {e}")
    
    @staticmethod
    def create_from_private_key(private_key_hex: str, ss58_format: int = 42) -> SDKKeypair:
        """
        Create keypair from private key
        
        Args:
            private_key_hex: Private key in hex format
            ss58_format: SS58 format for address encoding
            
        Returns:
            SDKKeypair object
        """
        try:
            keypair = Keypair.create_from_private_key(
                private_key_hex, 
                ss58_format=ss58_format
            )
            
            return SDKKeypair(
                mnemonic="",  # Not available when creating from private key
                private_key=keypair.private_key,
                public_key=keypair.public_key,
                address=keypair.ss58_address,
                ss58_format=ss58_format
            )
        except Exception as e:
            raise KeypairError(f"Failed to create keypair from private key: {e}")
    
    @staticmethod
    def create_new_account(words_count: int = 12, ss58_format: int = 42) -> SDKKeypair:
        """
        Create a new account with fresh keypair
        
        Args:
            words_count: Number of words in mnemonic
            ss58_format: SS58 format for address encoding
            
        Returns:
            SDKKeypair object
        """
        mnemonic = AccountManager.generate_mnemonic(words_count)
        return AccountManager.create_from_mnemonic(mnemonic, ss58_format)
    
    @staticmethod
    def validate_address(address: str, ss58_format: int = 42) -> bool:
        """
        Validate Creditcoin address format
        
        Args:
            address: Address to validate
            ss58_format: Expected SS58 format
            
        Returns:
            True if address is valid
        """
        try:
            keypair = Keypair(ss58_address=address, ss58_format=ss58_format)
            return keypair.ss58_address == address
        except:
            return False


class CreditScanClient:
    """
    Creditcoin Blockchain Scanner Client
    
    Provides an interface to interact with Creditcoin blockchain
    using substrateinterface.
    """
    
    def __init__(
        self, 
        url: str = "wss://mainnet.creditcoin.network/ws",
        timeout: int = 30,
        auto_reconnect: bool = True
    ):
        """
        Initialize the Creditcoin client
        
        Args:
            url: WebSocket URL of the Creditcoin node
            timeout: Request timeout in seconds
            auto_reconnect: Whether to auto-reconnect on connection loss
        """
        self.url = url
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        self._substrate = None
        self.account_manager = AccountManager()
        self._connect()
        self.credit_contracts = CreditContractManager(self)
    
    def _connect(self):
        """Establish connection to Creditcoin node"""
        try:
            self._substrate = SubstrateInterface(
                url=self.url,
                ss58_format=42,  # Creditcoin ss58 format
                type_registry_preset='default',
                auto_reconnect=self.auto_reconnect
            )
            logger.info(f"Connected to Creditcoin node: {self.url}")
        except Exception as e:
            raise NetworkError(f"Failed to connect to Creditcoin node: {e}")

    # Account Management Methods
    
    def create_account(self, words_count: int = 12) -> SDKKeypair:
        """
        Create a new Creditcoin account
        
        Args:
            words_count: Number of words in mnemonic phrase
            
        Returns:
            SDKKeypair object with account details
        """
        return self.account_manager.create_new_account(words_count)
    
    def import_account_from_mnemonic(self, mnemonic: str) -> SDKKeypair:
        """
        Import account from mnemonic phrase
        
        Args:
            mnemonic: Mnemonic phrase
            
        Returns:
            SDKKeypair object
        """
        return self.account_manager.create_from_mnemonic(mnemonic)
    
    def import_account_from_private_key(self, private_key_hex: str) -> SDKKeypair:
        """
        Import account from private key
        
        Args:
            private_key_hex: Private key in hex format
            
        Returns:
            SDKKeypair object
        """
        return self.account_manager.create_from_private_key(private_key_hex)
    
    def validate_address(self, address: str) -> bool:
        """
        Validate Creditcoin address format
        
        Args:
            address: Address to validate
            
        Returns:
            True if address is valid
        """
        return self.account_manager.validate_address(address)

    # Enhanced Balance Querying Methods
    
    def get_balance(self, address: str) -> TokenBalance:
        """
        Get detailed token balance for an address
        
        Args:
            address: Creditcoin address
            
        Returns:
            TokenBalance object with detailed balance information
        """
        if not self.validate_address(address):
            raise InvalidAddressError(f"Invalid Creditcoin address: {address}")
        
        try:
            account_info = self._substrate.query(
                module='System',
                storage_function='Account',
                params=[address]
            )
            
            if not account_info:
                return TokenBalance(
                    symbol="CTC",
                    balance=0,
                    locked=0,
                    reserved=0,
                    total=0,
                    decimals=18
                )
            
            data = account_info.value['data']
            free = float(data['free']) / 10**18
            reserved = float(data['reserved']) / 10**18
            misc_frozen = float(data['misc_frozen']) / 10**18
            fee_frozen = float(data['fee_frozen']) / 10**18
            
            balance = free
            locked = misc_frozen + fee_frozen
            total = free + reserved
            
            return TokenBalance(
                symbol="CTC",
                balance=balance,
                locked=locked,
                reserved=reserved,
                total=total,
                decimals=18
            )
            
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get balance: {e}")
    
    def get_balances_bulk(self, addresses: List[str]) -> Dict[str, TokenBalance]:
        """
        Get balances for multiple addresses in bulk
        
        Args:
            addresses: List of Creditcoin addresses
            
        Returns:
            Dictionary mapping addresses to TokenBalance objects
        """
        results = {}
        for address in addresses:
            try:
                results[address] = self.get_balance(address)
            except Exception as e:
                logger.warning(f"Failed to get balance for {address}: {e}")
                results[address] = TokenBalance(
                    symbol="CTC",
                    balance=0,
                    locked=0,
                    reserved=0,
                    total=0,
                    decimals=18
                )
        return results
    
    def get_account_info(self, address: str) -> AddressInfo:
        """
        Get comprehensive account information
        
        Args:
            address: Creditcoin address
            
        Returns:
            AddressInfo object with account details
        """
        balance = self.get_balance(address)
        
        try:
            account_info = self._substrate.query(
                module='System',
                storage_function='Account',
                params=[address]
            )
            
            nonce = account_info.value['nonce'] if account_info else 0
            
            return AddressInfo(
                address=address,
                balance=balance.balance,
                nonce=nonce,
                locked_balance=balance.locked,
                transaction_count=nonce  # Approximate
            )
            
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get account info: {e}")

    # Transaction Methods
    
    def get_transfer_fee_estimate(
        self, 
        from_address: str, 
        to_address: str, 
        amount: float
    ) -> float:
        """
        Estimate transfer fee
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            amount: Amount to transfer in CTC
            
        Returns:
            Estimated fee in CTC
        """
        try:
            keypair = Keypair(ss58_address=from_address)
            
            call = self._substrate.compose_call(
                call_module='Balances',
                call_function='transfer_keep_alive',
                call_params={
                    'dest': to_address,
                    'value': int(amount * 10**18)  # Convert to Planck
                }
            )
            
            payment_info = self._substrate.get_payment_info(call=call, keypair=keypair)
            
            if payment_info and 'partialFee' in payment_info:
                return float(payment_info['partialFee']) / 10**18
            else:
                return 0.01  # Default estimate
            
        except Exception as e:
            logger.warning(f"Failed to estimate fee: {e}")
            return 0.01  # Fallback estimate
    
    def transfer(
        self, 
        keypair: SDKKeypair, 
        to_address: str, 
        amount: float, 
        wait_for_inclusion: bool = True
    ) -> TransactionReceipt:
        """
        Transfer CTC tokens to another address
        
        Args:
            keypair: Sender's keypair
            to_address: Recipient address
            amount: Amount to transfer in CTC
            wait_for_inclusion: Whether to wait for transaction inclusion
            
        Returns:
            TransactionReceipt object
        """
        if not self.validate_address(to_address):
            raise InvalidAddressError(f"Invalid recipient address: {to_address}")
        
        # Check balance
        balance = self.get_balance(keypair.address)
        fee_estimate = self.get_transfer_fee_estimate(keypair.address, to_address, amount)
        
        if balance.balance < amount + fee_estimate:
            raise InsufficientBalanceError(
                f"Insufficient balance: {balance.balance} CTC available, "
                f"{amount} CTC + ~{fee_estimate:.6f} CTC fee required"
            )
        
        try:
            substrate_keypair = Keypair.create_from_private_key(
                keypair.private_key.hex(), 
                ss58_format=keypair.ss58_format
            )
            
            call = self._substrate.compose_call(
                call_module='Balances',
                call_function='transfer_keep_alive',
                call_params={
                    'dest': to_address,
                    'value': int(amount * 10**18)  # Convert to Planck
                }
            )
            
            extrinsic = self._substrate.create_signed_extrinsic(
                call=call, 
                keypair=substrate_keypair
            )
            
            result = self._substrate.submit_extrinsic(
                extrinsic, 
                wait_for_inclusion=wait_for_inclusion
            )
            
            if result.is_success:
                # Get transaction receipt details
                events = self._substrate.get_events(block_hash=result.block_hash)
                event_dicts = [event.value for event in events]
                
                # Calculate actual fee
                payment_info = self._substrate.get_payment_info(call=call, keypair=substrate_keypair)
                actual_fee = float(payment_info['partialFee']) / 10**18 if payment_info else fee_estimate
                
                return TransactionReceipt(
                    tx_hash=result.extrinsic_hash,
                    block_hash=result.block_hash,
                    block_number=result.block_number,
                    status='success',
                    events=event_dicts,
                    fee=actual_fee,
                    timestamp=self._substrate.get_block_timestamp(block_hash=result.block_hash)
                )
            else:
                raise TransactionError(f"Transaction failed: {result.error_message}")
                
        except SubstrateRequestException as e:
            raise TransactionError(f"Transfer failed: {e}")
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction status by hash
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction status information
        """
        try:
            result = self._substrate.retrieve_extrinsic_by_identifier(tx_hash)
            return {
                'hash': tx_hash,
                'block_hash': result.block_hash,
                'block_number': result.block_number,
                'success': result.is_success,
                'error_message': result.error_message,
                'events': [event.value for event in result.events]
            }
        except Exception as e:
            raise TransactionError(f"Failed to get transaction status: {e}")
        
    # Add these convenience methods
    def create_lend_offer(
        self,
        keypair: SDKKeypair,
        principal: float,
        interest_rate: float,
        duration_days: int,
        collateral_required: bool = False,
        collateral_amount: Optional[float] = None,
        expiry_blocks: int = 14400
    ) -> TransactionReceipt:
        """
        Convenience method to create a lend offer (ask order)
        """
        terms = LoanTerms(
            principal=principal,
            interest_rate=interest_rate,
            duration_days=duration_days,
            collateral_required=collateral_required,
            collateral_amount=collateral_amount
        )
        
        return self.credit_contracts.create_ask_order(
            keypair=keypair,
            terms=terms,
            expiry_blocks=expiry_blocks
        )
    
    def create_borrow_request(
        self,
        keypair: SDKKeypair,
        principal: float,
        interest_rate: float,
        duration_days: int,
        collateral_required: bool = False,
        collateral_amount: Optional[float] = None,
        expiry_blocks: int = 14400
    ) -> TransactionReceipt:
        """
        Convenience method to create a borrow request (bid order)
        """
        terms = LoanTerms(
            principal=principal,
            interest_rate=interest_rate,
            duration_days=duration_days,
            collateral_required=collateral_required,
            collateral_amount=collateral_amount
        )
        
        return self.credit_contracts.create_bid_order(
            keypair=keypair,
            terms=terms,
            expiry_blocks=expiry_blocks
        )

    # Existing methods remain the same...
    def get_network_stats(self) -> NetworkStats:
        """Get network statistics"""
        # ... existing implementation

    def get_address_info(self, address: str) -> AddressInfo:
        """Get information about a Creditcoin address"""
        # ... existing implementation

    def get_block_info(self, block_number: Optional[int] = None) -> BlockInfo:
        """Get block information"""
        # ... existing implementation

    def get_transactions_by_address(self, address: str, limit: int = 50) -> List[Transaction]:
        """Get transactions for a specific address"""
        # ... existing implementation

    def get_ask_orders(self, address: Optional[str] = None) -> List[AskOrder]:
        """Get ask orders, optionally filtered by address"""
        # ... existing implementation

    def get_bid_orders(self, address: Optional[str] = None) -> List[BidOrder]:
        """Get bid orders, optionally filtered by address"""
        # ... existing implementation

    def get_deal_orders(self) -> List[DealOrder]:
        """Get deal orders"""
        # ... existing implementation

    def _is_valid_address(self, address: str) -> bool:
        """Validate Creditcoin address format"""
        return self.validate_address(address)

    def close(self):
        """Close the connection"""
        if self._substrate:
            self._substrate.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()