from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class AddressInfo:
    """Information about a Creditcoin address"""
    address: str
    balance: float
    nonce: int
    locked_balance: float
    transaction_count: int
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'AddressInfo':
        return cls(
            address=data['address'],
            balance=data.get('balance', 0),
            nonce=data.get('nonce', 0),
            locked_balance=data.get('locked_balance', 0),
            transaction_count=data.get('transaction_count', 0)
        )

@dataclass
class Transaction:
    """Creditcoin transaction information"""
    hash: str
    block_number: int
    timestamp: datetime
    from_address: str
    to_address: str
    value: float
    fee: float
    status: str
    method: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(
            hash=data['hash'],
            block_number=data['block_number'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            from_address=data['from_address'],
            to_address=data['to_address'],
            value=data['value'],
            fee=data.get('fee', 0),
            status=data['status'],
            method=data.get('method'),
            parameters=data.get('parameters')
        )

@dataclass
class BlockInfo:
    """Block information"""
    number: int
    hash: str
    timestamp: datetime
    parent_hash: str
    state_root: str
    extrinsics_root: str
    validator: Optional[str]
    transaction_count: int
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'BlockInfo':
        return cls(
            number=data['number'],
            hash=data['hash'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            parent_hash=data['parent_hash'],
            state_root=data['state_root'],
            extrinsics_root=data['extrinsics_root'],
            validator=data.get('validator'),
            transaction_count=data.get('transaction_count', 0)
        )

@dataclass
class NetworkStats:
    """Network statistics"""
    current_block: int
    total_blocks: int
    total_addresses: int
    total_transactions: int
    active_validators: int
    average_block_time: float
    network_version: str
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'NetworkStats':
        return cls(
            current_block=data['current_block'],
            total_blocks=data['total_blocks'],
            total_addresses=data.get('total_addresses', 0),
            total_transactions=data.get('total_transactions', 0),
            active_validators=data.get('active_validators', 0),
            average_block_time=data.get('average_block_time', 0),
            network_version=data.get('network_version', 'unknown')
        )

@dataclass
class AskOrder:
    """Ask order information"""
    order_id: str
    address: str
    amount: float
    fee: float
    expiry: Optional[datetime]
    block_number: int
    status: str
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'AskOrder':
        expiry = None
        if data.get('expiry'):
            expiry = datetime.fromisoformat(data['expiry'].replace('Z', '+00:00'))
        return cls(
            order_id=data['order_id'],
            address=data['address'],
            amount=data['amount'],
            fee=data.get('fee', 0),
            expiry=expiry,
            block_number=data['block_number'],
            status=data['status']
        )

@dataclass
class BidOrder:
    """Bid order information"""
    order_id: str
    address: str
    amount: float
    fee: float
    expiry: Optional[datetime]
    block_number: int
    status: str
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'BidOrder':
        expiry = None
        if data.get('expiry'):
            expiry = datetime.fromisoformat(data['expiry'].replace('Z', '+00:00'))
        return cls(
            order_id=data['order_id'],
            address=data['address'],
            amount=data['amount'],
            fee=data.get('fee', 0),
            expiry=expiry,
            block_number=data['block_number'],
            status=data['status']
        )

@dataclass
class DealOrder:
    """Deal order information"""
    deal_id: str
    ask_order_id: str
    bid_order_id: str
    amount: float
    block_number: int
    status: str
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'DealOrder':
        return cls(
            deal_id=data['deal_id'],
            ask_order_id=data['ask_order_id'],
            bid_order_id=data['bid_order_id'],
            amount=data['amount'],
            block_number=data['block_number'],
            status=data['status']
        )