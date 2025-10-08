import pytest
from unittest.mock import Mock, patch
from credit_scan_sdk import CreditScanClient, AccountManager
from credit_scan_sdk.models import Keypair
from credit_scan_sdk.exceptions import KeypairError, InvalidAddressError, InsufficientBalanceError

class TestAccountManagement:
    
    @pytest.fixture
    def client(self):
        with patch('credit_scan_sdk.client.SubstrateInterface'):
            return CreditScanClient()
    
    def test_generate_mnemonic(self):
        mnemonic = AccountManager.generate_mnemonic(12)
        assert len(mnemonic.split()) == 12
        
        mnemonic24 = AccountManager.generate_mnemonic(24)
        assert len(mnemonic24.split()) == 24
    
    def test_create_from_mnemonic(self):
        mnemonic = "word " * 11 + "word"  # 12 words
        keypair = AccountManager.create_from_mnemonic(mnemonic)
        
        assert isinstance(keypair, Keypair)
        assert keypair.mnemonic == mnemonic
        assert keypair.address.startswith('5')
    
    def test_create_new_account(self, client):
        keypair = client.create_account(12)
        
        assert isinstance(keypair, Keypair)
        assert len(keypair.mnemonic.split()) == 12
        assert keypair.address.startswith('5')
    
    def test_import_from_mnemonic(self, client):
        mnemonic = "test " * 11 + "test"
        keypair = client.import_account_from_mnemonic(mnemonic)
        
        assert keypair.mnemonic == mnemonic
    
    def test_validate_address(self, client):
        # Valid address format (this is a test address)
        test_address = "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
        assert client.validate_address(test_address)
        
        # Invalid address
        assert not client.validate_address("invalid_address")
    
    def test_get_balance(self, client):
        with patch.object(client, '_substrate') as mock_substrate:
            mock_substrate.query.return_value = Mock(value={
                'data': {
                    'free': 1000000000000000000,  # 1 CTC
                    'reserved': 500000000000000000,  # 0.5 CTC
                    'misc_frozen': 100000000000000000,  # 0.1 CTC
                    'fee_frozen': 50000000000000000  # 0.05 CTC
                },
                'nonce': 5
            })
            
            balance = client.get_balance("5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")
            
            assert balance.balance == 1.0  # free
            assert balance.reserved == 0.5
            assert balance.locked == 0.15  # misc_frozen + fee_frozen
            assert balance.total == 1.5  # free + reserved
    
    def test_transfer_insufficient_balance(self, client):
        keypair = Keypair(
            mnemonic="test",
            private_key=b"test",
            public_key=b"test",
            address="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
        )
        
        with patch.object(client, 'get_balance') as mock_balance:
            mock_balance.return_value = Mock(balance=0.5)  # Only 0.5 CTC available
            
            with patch.object(client, 'get_transfer_fee_estimate') as mock_fee:
                mock_fee.return_value = 0.01  # 0.01 CTC fee
                
                with pytest.raises(InsufficientBalanceError):
                    client.transfer(keypair, "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty", 1.0)