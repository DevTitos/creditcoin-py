#!/usr/bin/env python3
"""
Example of using Creditcoin credit marketplace functionality
"""

from creditcoin.client import CreditScanClient
from creditcoin.credit_contracts import LoanTerms, OrderType, OrderStatus

def main():
    # Connect to Creditcoin
    client = CreditScanClient()
    
    # Create accounts (in real usage, use existing accounts)
    lender = client.create_account()
    borrower = client.create_account()
    
    print(f"Lender: {lender.address}")
    print(f"Borrower: {borrower.address}")
    
    # Lender creates an offer to lend
    print("\n1. Creating lend offer...")
    lend_terms = LoanTerms(
        principal=1000.0,  # 1000 CTC
        interest_rate=5.0,  # 5% APR
        duration_days=90,   # 90 days
        collateral_required=True,
        collateral_amount=1200.0  # 120% collateral
    )
    
    receipt = client.credit_contracts.create_ask_order(
        keypair=lender,
        terms=lend_terms,
        expiry_blocks=14400  # 24 hours
    )
    print(f"Lend offer created: {receipt.tx_hash}")
    
    # Borrower creates a borrow request
    print("\n2. Creating borrow request...")
    borrow_terms = LoanTerms(
        principal=800.0,    # 800 CTC
        interest_rate=7.0,  # 7% APR
        duration_days=60,   # 60 days
        collateral_required=True,
        collateral_amount=1000.0  # 125% collateral
    )
    
    receipt = client.credit_contracts.create_bid_order(
        keypair=borrower,
        terms=borrow_terms,
        expiry_blocks=14400
    )
    print(f"Borrow request created: {receipt.tx_hash}")
    
    # Get active orders
    print("\n3. Active orders:")
    ask_orders = client.credit_contracts.get_ask_orders(status=OrderStatus.ACTIVE)
    bid_orders = client.credit_contracts.get_bid_orders(status=OrderStatus.ACTIVE)
    
    print(f"Active lend offers: {len(ask_orders)}")
    print(f"Active borrow requests: {len(bid_orders)}")
    
    # Borrower accepts a lend offer (simplified)
    if ask_orders:
        order_id = ask_orders[0].order_id
        print(f"\n4. Accepting lend offer {order_id}...")
        
        receipt = client.credit_contracts.accept_offer(
            keypair=borrower,
            order_id=order_id,
            order_type=OrderType.ASK
        )
        print(f"Offer accepted: {receipt.tx_hash}")
    
    # Get credit deals
    print("\n5. Credit deals:")
    deals = client.credit_contracts.get_credit_deals()
    for deal in deals:
        print(f"Deal {deal.deal_id}: {deal.lender_address} -> {deal.borrower_address}")
        print(f"  Amount: {deal.amount} CTC, Status: {deal.status}")

if __name__ == "__main__":
    main()