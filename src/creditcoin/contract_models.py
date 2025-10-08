from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class OrderType(Enum):
    ASK = "ask"
    BID = "bid"

class OrderStatus(Enum):
    ACTIVE = "active"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class DealStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

@dataclass
class LoanTerms:
    """Loan terms for credit agreements"""
    principal: float
    interest_rate: float  # Annual percentage rate
    duration_days: int
    collateral_required: bool
    collateral_amount: Optional[float] = None
    grace_period_days: int = 0
    late_fee_percentage: float = 0.0

@dataclass
class CreditAskOrder:
    """Ask order (lender offering credit)"""
    order_id: str
    lender_address: str
    terms: LoanTerms
    expiry_block: int
    status: OrderStatus
    created_block: int
    filled_amount: float = 0.0

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'CreditAskOrder':
        return cls(
            order_id=data['order_id'],
            lender_address=data['lender_address'],
            terms=LoanTerms(**data['terms']),
            expiry_block=data['expiry_block'],
            status=OrderStatus(data['status']),
            created_block=data['created_block'],
            filled_amount=data.get('filled_amount', 0.0)
        )

@dataclass
class CreditBidOrder:
    """Bid order (borrower seeking credit)"""
    order_id: str
    borrower_address: str
    terms: LoanTerms
    expiry_block: int
    status: OrderStatus
    created_block: int
    filled_amount: float = 0.0

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'CreditBidOrder':
        return cls(
            order_id=data['order_id'],
            borrower_address=data['borrower_address'],
            terms=LoanTerms(**data['terms']),
            expiry_block=data['expiry_block'],
            status=OrderStatus(data['status']),
            created_block=data['created_block'],
            filled_amount=data.get('filled_amount', 0.0)
        )

@dataclass
class CreditDeal:
    """Credit deal between lender and borrower"""
    deal_id: str
    ask_order_id: str
    bid_order_id: str
    lender_address: str
    borrower_address: str
    terms: LoanTerms
    amount: float
    status: DealStatus
    created_block: int
    start_block: Optional[int] = None
    end_block: Optional[int] = None
    repaid_amount: float = 0.0

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'CreditDeal':
        return cls(
            deal_id=data['deal_id'],
            ask_order_id=data['ask_order_id'],
            bid_order_id=data['bid_order_id'],
            lender_address=data['lender_address'],
            borrower_address=data['borrower_address'],
            terms=LoanTerms(**data['terms']),
            amount=data['amount'],
            status=DealStatus(data['status']),
            created_block=data['created_block'],
            start_block=data.get('start_block'),
            end_block=data.get('end_block'),
            repaid_amount=data.get('repaid_amount', 0.0)
        )

@dataclass
class RepaymentSchedule:
    """Loan repayment schedule"""
    deal_id: str
    total_amount: float
    principal: float
    interest: float
    due_date: datetime
    status: str  # pending, paid, overdue

@dataclass
class CollateralInfo:
    """Collateral information for loans"""
    deal_id: str
    collateral_amount: float
    collateral_asset: str
    locked_block: int
    release_block: Optional[int] = None
    liquidated: bool = False