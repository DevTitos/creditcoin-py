import logging
from typing import Optional, List, Dict, Any, Union
from substrateinterface import Keypair
from substrateinterface.exceptions import SubstrateRequestException

from .models import Keypair as SDKKeypair, TransactionReceipt
from .contract_models import (
    LoanTerms, CreditAskOrder, CreditBidOrder, CreditDeal, 
    OrderType, OrderStatus, DealStatus
)
from .exceptions import (
    CreditScanError, TransactionError, InsufficientBalanceError
)

logger = logging.getLogger(__name__)


class CreditContractManager:
    """
    Manager for Creditcoin's credit marketplace functionality
    
    This class provides methods to create and manage credit agreements,
    which are the closest concept to "contracts" on Creditcoin.
    """
    
    def __init__(self, client):
        self.client = client
        self._substrate = client._substrate

    def create_ask_order(
        self,
        keypair: SDKKeypair,
        terms: LoanTerms,
        expiry_blocks: int = 14400,  # ~24 hours at 6s blocks
        wait_for_inclusion: bool = True
    ) -> TransactionReceipt:
        """
        Create an ask order (offer to lend)
        
        Args:
            keypair: Lender's keypair
            terms: Loan terms
            expiry_blocks: Order expiry in blocks
            wait_for_inclusion: Wait for transaction inclusion
            
        Returns:
            TransactionReceipt
        """
        try:
            substrate_keypair = Keypair.create_from_private_key(
                keypair.private_key.hex(), 
                ss58_format=keypair.ss58_format
            )
            
            # Convert terms to blockchain format
            call_params = {
                'principal': int(terms.principal * 10**18),  # Convert to Planck
                'interest_rate': int(terms.interest_rate * 100),  # Convert to basis points
                'duration': terms.duration_days,
                'collateral_required': terms.collateral_required,
                'expiry': expiry_blocks
            }
            
            if terms.collateral_required and terms.collateral_amount:
                call_params['collateral_amount'] = int(terms.collateral_amount * 10**18)
            
            call = self._substrate.compose_call(
                call_module='Credit',  # Assuming Credit pallet exists
                call_function='create_ask_order',
                call_params=call_params
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
                return self._create_transaction_receipt(result, substrate_keypair, call)
            else:
                raise TransactionError(f"Ask order creation failed: {result.error_message}")
                
        except SubstrateRequestException as e:
            raise TransactionError(f"Ask order creation failed: {e}")

    def create_bid_order(
        self,
        keypair: SDKKeypair,
        terms: LoanTerms,
        expiry_blocks: int = 14400,
        wait_for_inclusion: bool = True
    ) -> TransactionReceipt:
        """
        Create a bid order (request to borrow)
        
        Args:
            keypair: Borrower's keypair
            terms: Loan terms
            expiry_blocks: Order expiry in blocks
            wait_for_inclusion: Wait for transaction inclusion
            
        Returns:
            TransactionReceipt
        """
        try:
            substrate_keypair = Keypair.create_from_private_key(
                keypair.private_key.hex(), 
                ss58_format=keypair.ss58_format
            )
            
            call_params = {
                'principal': int(terms.principal * 10**18),
                'interest_rate': int(terms.interest_rate * 100),
                'duration': terms.duration_days,
                'collateral_required': terms.collateral_required,
                'expiry': expiry_blocks
            }
            
            if terms.collateral_required and terms.collateral_amount:
                call_params['collateral_amount'] = int(terms.collateral_amount * 10**18)
            
            call = self._substrate.compose_call(
                call_module='Credit',
                call_function='create_bid_order',
                call_params=call_params
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
                return self._create_transaction_receipt(result, substrate_keypair, call)
            else:
                raise TransactionError(f"Bid order creation failed: {result.error_message}")
                
        except SubstrateRequestException as e:
            raise TransactionError(f"Bid order creation failed: {e}")

    def accept_offer(
        self,
        keypair: SDKKeypair,
        order_id: str,
        order_type: OrderType,
        wait_for_inclusion: bool = True
    ) -> TransactionReceipt:
        """
        Accept an ask or bid order to create a credit deal
        
        Args:
            keypair: Counterparty's keypair
            order_id: Order ID to accept
            order_type: Type of order (ASK or BID)
            wait_for_inclusion: Wait for transaction inclusion
            
        Returns:
            TransactionReceipt
        """
        try:
            substrate_keypair = Keypair.create_from_private_key(
                keypair.private_key.hex(), 
                ss58_format=keypair.ss58_format
            )
            
            if order_type == OrderType.ASK:
                call_function = 'accept_ask_order'
            else:
                call_function = 'accept_bid_order'
            
            call = self._substrate.compose_call(
                call_module='Credit',
                call_function=call_function,
                call_params={'order_id': order_id}
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
                return self._create_transaction_receipt(result, substrate_keypair, call)
            else:
                raise TransactionError(f"Offer acceptance failed: {result.error_message}")
                
        except SubstrateRequestException as e:
            raise TransactionError(f"Offer acceptance failed: {e}")

    def repay_loan(
        self,
        keypair: SDKKeypair,
        deal_id: str,
        amount: float,
        wait_for_inclusion: bool = True
    ) -> TransactionReceipt:
        """
        Make a loan repayment
        
        Args:
            keypair: Borrower's keypair
            deal_id: Deal ID to repay
            amount: Amount to repay in CTC
            wait_for_inclusion: Wait for transaction inclusion
            
        Returns:
            TransactionReceipt
        """
        try:
            substrate_keypair = Keypair.create_from_private_key(
                keypair.private_key.hex(), 
                ss58_format=keypair.ss58_format
            )
            
            call = self._substrate.compose_call(
                call_module='Credit',
                call_function='repay_loan',
                call_params={
                    'deal_id': deal_id,
                    'amount': int(amount * 10**18)
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
                return self._create_transaction_receipt(result, substrate_keypair, call)
            else:
                raise TransactionError(f"Loan repayment failed: {result.error_message}")
                
        except SubstrateRequestException as e:
            raise TransactionError(f"Loan repayment failed: {e}")

    def get_ask_orders(
        self, 
        lender_address: Optional[str] = None,
        status: Optional[OrderStatus] = None
    ) -> List[CreditAskOrder]:
        """
        Get ask orders with filtering
        
        Args:
            lender_address: Filter by lender address
            status: Filter by order status
            
        Returns:
            List of CreditAskOrder objects
        """
        try:
            # This would query the blockchain storage for ask orders
            storage_key = self._substrate.create_storage_key(
                module='Credit',
                storage_function='AskOrders'
            )
            
            orders = []
            for key, value in self._substrate.query_map(storage_key):
                order_data = {
                    'order_id': str(key),
                    'lender_address': value['lender'],
                    'terms': {
                        'principal': float(value['principal']) / 10**18,
                        'interest_rate': float(value['interest_rate']) / 100,
                        'duration_days': value['duration'],
                        'collateral_required': value['collateral_required'],
                        'collateral_amount': float(value.get('collateral_amount', 0)) / 10**18
                    },
                    'expiry_block': value['expiry'],
                    'status': OrderStatus(value['status']),
                    'created_block': value['created_block'],
                    'filled_amount': float(value.get('filled_amount', 0)) / 10**18
                }
                
                order = CreditAskOrder.from_json(order_data)
                
                # Apply filters
                if lender_address and order.lender_address != lender_address:
                    continue
                if status and order.status != status:
                    continue
                    
                orders.append(order)
            
            return orders
            
        except SubstrateRequestException as e:
            logger.error(f"Failed to get ask orders: {e}")
            return []

    def get_bid_orders(
        self, 
        borrower_address: Optional[str] = None,
        status: Optional[OrderStatus] = None
    ) -> List[CreditBidOrder]:
        """
        Get bid orders with filtering
        
        Args:
            borrower_address: Filter by borrower address
            status: Filter by order status
            
        Returns:
            List of CreditBidOrder objects
        """
        try:
            storage_key = self._substrate.create_storage_key(
                module='Credit',
                storage_function='BidOrders'
            )
            
            orders = []
            for key, value in self._substrate.query_map(storage_key):
                order_data = {
                    'order_id': str(key),
                    'borrower_address': value['borrower'],
                    'terms': {
                        'principal': float(value['principal']) / 10**18,
                        'interest_rate': float(value['interest_rate']) / 100,
                        'duration_days': value['duration'],
                        'collateral_required': value['collateral_required'],
                        'collateral_amount': float(value.get('collateral_amount', 0)) / 10**18
                    },
                    'expiry_block': value['expiry'],
                    'status': OrderStatus(value['status']),
                    'created_block': value['created_block'],
                    'filled_amount': float(value.get('filled_amount', 0)) / 10**18
                }
                
                order = CreditBidOrder.from_json(order_data)
                
                # Apply filters
                if borrower_address and order.borrower_address != borrower_address:
                    continue
                if status and order.status != status:
                    continue
                    
                orders.append(order)
            
            return orders
            
        except SubstrateRequestException as e:
            logger.error(f"Failed to get bid orders: {e}")
            return []

    def get_credit_deals(
        self,
        participant_address: Optional[str] = None,
        status: Optional[DealStatus] = None
    ) -> List[CreditDeal]:
        """
        Get credit deals with filtering
        
        Args:
            participant_address: Filter by lender or borrower address
            status: Filter by deal status
            
        Returns:
            List of CreditDeal objects
        """
        try:
            storage_key = self._substrate.create_storage_key(
                module='Credit',
                storage_function='Deals'
            )
            
            deals = []
            for key, value in self._substrate.query_map(storage_key):
                deal_data = {
                    'deal_id': str(key),
                    'ask_order_id': str(value['ask_order_id']),
                    'bid_order_id': str(value['bid_order_id']),
                    'lender_address': value['lender'],
                    'borrower_address': value['borrower'],
                    'terms': {
                        'principal': float(value['principal']) / 10**18,
                        'interest_rate': float(value['interest_rate']) / 100,
                        'duration_days': value['duration'],
                        'collateral_required': value['collateral_required'],
                        'collateral_amount': float(value.get('collateral_amount', 0)) / 10**18
                    },
                    'amount': float(value['amount']) / 10**18,
                    'status': DealStatus(value['status']),
                    'created_block': value['created_block'],
                    'start_block': value.get('start_block'),
                    'end_block': value.get('end_block'),
                    'repaid_amount': float(value.get('repaid_amount', 0)) / 10**18
                }
                
                deal = CreditDeal.from_json(deal_data)
                
                # Apply filters
                if (participant_address and 
                    deal.lender_address != participant_address and 
                    deal.borrower_address != participant_address):
                    continue
                if status and deal.status != status:
                    continue
                    
                deals.append(deal)
            
            return deals
            
        except SubstrateRequestException as e:
            logger.error(f"Failed to get credit deals: {e}")
            return []

    def _create_transaction_receipt(self, result, keypair, call) -> TransactionReceipt:
        """Create transaction receipt from result"""
        events = self._substrate.get_events(block_hash=result.block_hash)
        event_dicts = [event.value for event in events]
        
        payment_info = self._substrate.get_payment_info(call=call, keypair=keypair)
        actual_fee = float(payment_info['partialFee']) / 10**18 if payment_info else 0
        
        return TransactionReceipt(
            tx_hash=result.extrinsic_hash,
            block_hash=result.block_hash,
            block_number=result.block_number,
            status='success',
            events=event_dicts,
            fee=actual_fee,
            timestamp=self._substrate.get_block_timestamp(block_hash=result.block_hash)
        )