# creditcoin-py

A Python SDK for interacting with the Creditcoin blockchain using substrateinterface.

## Features

- 🔐 **Account Management**: Create, import, and manage Creditcoin accounts
- 💰 **Balance Querying**: Get detailed token balances and transaction history
- 📊 **Network Statistics**: Access real-time blockchain statistics
- 🤝 **Credit Marketplace**: Create and manage lend/borrow orders
- 📜 **Transaction Management**: Send transactions with fee estimation
- 🔍 **Block Explorer**: Query blocks, transactions, and addresses
- 🛡️ **Security**: Built-in validation and error handling
- 🚀 **Async Support**: Full asynchronous operation support


## Installation

pip install creditcoin-py

## Account Management

### Creating Accounts

```python
from creditcoin import CreditScanClient

client = CreditScanClient()

# Create a new account
new_account = client.create_account(words_count=12)
print(f"New address: {new_account.address}")
print(f"Mnemonic: {new_account.mnemonic}")  # Store securely!

# Import existing account from mnemonic
imported_account = client.import_account_from_mnemonic("your mnemonic phrase here")

# Import from private key
imported_account = client.import_account_from_private_key("0x...")

# Get detailed balance
balance = client.get_balance("5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")
print(f"Available: {balance.balance} CTC")
print(f"Locked: {balance.locked} CTC")
print(f"Reserved: {balance.reserved} CTC")

# Get balances for multiple addresses
addresses = ["addr1", "addr2", "addr3"]
balances = client.get_balances_bulk(addresses)
for addr, bal in balances.items():
    print(f"{addr}: {bal.balance} CTC")

# Transfer tokens
receipt = client.transfer(
    keypair=my_keypair,
    to_address="recipient_address",
    amount=10.5,  # CTC
    wait_for_inclusion=True
)
print(f"Transaction hash: {receipt.tx_hash}")
print(f"Fee: {receipt.fee} CTC")


# Estimate transfer fee
fee = client.get_transfer_fee_estimate(
    from_address="sender_address",
    to_address="recipient_address", 
    amount=10.0
)
print(f"Estimated fee: {fee:.6f} CTC")
```