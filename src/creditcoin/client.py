import json
import logging
from typing import Optional, List, Dict, Any, Union
from substrateinterface import SubstrateInterface
from substrateinterface.exceptions import SubstrateRequestException

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

logger = logging.getLogger(__name__)

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
        self._connect()
    
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
    
    def get_network_stats(self) -> NetworkStats:
        """Get network statistics"""
        try:
            chain_properties = self._substrate.properties
            finalized_head = self._substrate.get_chain_finalised_head()
            finalized_block = self._substrate.get_block(block_hash=finalized_head)
            
            # Get validator count (approximate)
            validators = self._substrate.query(
                module='Session',
                storage_function='Validators'
            )
            
            return NetworkStats(
                current_block=finalized_block['header']['number'],
                total_blocks=finalized_block['header']['number'],
                total_addresses=0,  # Would need custom indexing
                total_transactions=0,  # Would need custom indexing
                active_validators=len(validators) if validators else 0,
                average_block_time=6.0,  # Creditcoin target block time
                network_version=chain_properties.get('ss58Format', 'unknown')
            )
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get network stats: {e}")
    
    def get_address_info(self, address: str) -> AddressInfo:
        """
        Get information about a Creditcoin address
        
        Args:
            address: Creditcoin address in SS58 format
            
        Returns:
            AddressInfo object with address details
        """
        try:
            # Validate address format
            if not self._is_valid_address(address):
                raise InvalidAddressError(f"Invalid Creditcoin address: {address}")
            
            # Get account info
            account_info = self._substrate.query(
                module='System',
                storage_function='Account',
                params=[address]
            )
            
            if not account_info:
                return AddressInfo(
                    address=address,
                    balance=0,
                    nonce=0,
                    locked_balance=0,
                    transaction_count=0
                )
            
            # Extract balance information
            data = account_info.value['data']
            free = float(data['free']) / 10**18  # Convert to CTC
            reserved = float(data['reserved']) / 10**18
            misc_frozen = float(data['misc_frozen']) / 10**18
            fee_frozen = float(data['fee_frozen']) / 10**18
            
            balance = free + reserved
            locked_balance = misc_frozen + fee_frozen
            
            return AddressInfo(
                address=address,
                balance=balance,
                nonce=account_info.value['nonce'],
                locked_balance=locked_balance,
                transaction_count=account_info.value['nonce']  # Approximate
            )
            
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get address info: {e}")
    
    def get_block_info(self, block_number: Optional[int] = None) -> BlockInfo:
        """
        Get block information
        
        Args:
            block_number: Specific block number, None for latest block
            
        Returns:
            BlockInfo object with block details
        """
        try:
            if block_number:
                block_hash = self._substrate.get_block_hash(block_number)
                block = self._substrate.get_block(block_hash=block_hash)
            else:
                block = self._substrate.get_block()
            
            header = block['header']
            
            # Get validator information
            validator = None
            if block_number:
                # Try to get validator from session module
                try:
                    validators = self._substrate.query(
                        module='Session',
                        storage_function='Validators',
                        block_hash=block_hash
                    )
                    if validators:
                        # Simplified - in reality you'd need to map to block author
                        validator = validators[0] if validators else None
                except:
                    pass
            
            return BlockInfo(
                number=header['number'],
                hash=block['header']['hash'],
                timestamp=self._substrate.get_block_timestamp(block_hash=block['header']['hash']),
                parent_hash=header['parentHash'],
                state_root=header['stateRoot'],
                extrinsics_root=header['extrinsicsRoot'],
                validator=validator,
                transaction_count=len(block['extrinsics'])
            )
            
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get block info: {e}")
    
    def get_transactions_by_address(
        self, 
        address: str, 
        limit: int = 50
    ) -> List[Transaction]:
        """
        Get transactions for a specific address
        
        Note: This is a simplified implementation. For production use,
        you would need to index transactions or use a block explorer API.
        
        Args:
            address: Creditcoin address
            limit: Maximum number of transactions to return
            
        Returns:
            List of Transaction objects
        """
        # This is a placeholder implementation
        # In production, you'd need to scan blocks or use an indexed service
        logger.warning("Transaction scanning requires block indexing for production use")
        return []
    
    def get_ask_orders(self, address: Optional[str] = None) -> List[AskOrder]:
        """Get ask orders, optionally filtered by address"""
        try:
            # Query ask orders from Creditcoin pallet
            storage_key = self._substrate.create_storage_key(
                module='Credit',
                storage_function='AskOrders'
            )
            
            ask_orders = []
            for key, value in self._substrate.query_map(storage_key):
                order = AskOrder.from_json({
                    'order_id': str(key),
                    'address': value['who'],
                    'amount': float(value['amount']) / 10**18,
                    'fee': float(value['fee']) / 10**18,
                    'expiry': value.get('expiry'),
                    'block_number': value['created_block'],
                    'status': 'active'  # Simplified
                })
                
                if not address or order.address == address:
                    ask_orders.append(order)
            
            return ask_orders
            
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get ask orders: {e}")
    
    def get_bid_orders(self, address: Optional[str] = None) -> List[BidOrder]:
        """Get bid orders, optionally filtered by address"""
        try:
            # Query bid orders from Creditcoin pallet
            storage_key = self._substrate.create_storage_key(
                module='Credit',
                storage_function='BidOrders'
            )
            
            bid_orders = []
            for key, value in self._substrate.query_map(storage_key):
                order = BidOrder.from_json({
                    'order_id': str(key),
                    'address': value['who'],
                    'amount': float(value['amount']) / 10**18,
                    'fee': float(value['fee']) / 10**18,
                    'expiry': value.get('expiry'),
                    'block_number': value['created_block'],
                    'status': 'active'  # Simplified
                })
                
                if not address or order.address == address:
                    bid_orders.append(order)
            
            return bid_orders
            
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get bid orders: {e}")
    
    def get_deal_orders(self) -> List[DealOrder]:
        """Get deal orders"""
        try:
            # Query deal orders from Creditcoin pallet
            storage_key = self._substrate.create_storage_key(
                module='Credit',
                storage_function='DealOrders'
            )
            
            deal_orders = []
            for key, value in self._substrate.query_map(storage_key):
                order = DealOrder.from_json({
                    'deal_id': str(key),
                    'ask_order_id': str(value['ask_order_id']),
                    'bid_order_id': str(value['bid_order_id']),
                    'amount': float(value['amount']) / 10**18,
                    'block_number': value['created_block'],
                    'status': 'active'  # Simplified
                })
                
                deal_orders.append(order)
            
            return deal_orders
            
        except SubstrateRequestException as e:
            raise NetworkError(f"Failed to get deal orders: {e}")
    
    def _is_valid_address(self, address: str) -> bool:
        """Validate Creditcoin address format"""
        try:
            self._substrate.decode_address(address)
            return True
        except:
            return False
    
    def close(self):
        """Close the connection"""
        if self._substrate:
            self._substrate.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()