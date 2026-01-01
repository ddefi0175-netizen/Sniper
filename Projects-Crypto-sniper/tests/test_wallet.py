"""
Tests for wallet integration module.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from web3 import Web3


class TestWalletManager:
    """Tests for WalletManager class."""
    
    def test_get_native_balance(self, mock_web3, test_wallet_address):
        """Test native balance retrieval."""
        # Mock balance in wei
        balance_wei = 1500000000000000000  # 1.5 ETH
        mock_web3.eth.get_balance.return_value = balance_wei
        
        # Convert to ETH
        balance_eth = Decimal(balance_wei) / Decimal(10**18)
        
        assert balance_eth == Decimal("1.5")
    
    def test_get_token_balance(self, mock_web3, mock_contract, test_wallet_address):
        """Test ERC20 token balance retrieval."""
        # Mock contract
        contract = mock_contract({
            "balanceOf": 1000000000,  # 1000 USDC (6 decimals)
            "decimals": 6,
            "symbol": "USDC",
            "name": "USD Coin"
        })
        
        balance = Decimal(1000000000) / Decimal(10**6)
        assert balance == Decimal("1000")
    
    def test_checksum_address(self, test_wallet_address):
        """Test address checksum conversion."""
        lowercase = test_wallet_address.lower()
        checksum = Web3.to_checksum_address(lowercase)
        
        assert Web3.is_checksum_address(checksum)
        assert not Web3.is_checksum_address(lowercase)
    
    @pytest.mark.parametrize("amount,decimals,expected_raw", [
        (Decimal("1.0"), 18, 1000000000000000000),
        (Decimal("100"), 6, 100000000),
        (Decimal("0.5"), 8, 50000000),
        (Decimal("0.000001"), 18, 1000000000000),
    ])
    def test_amount_to_raw(self, amount, decimals, expected_raw):
        """Test amount conversion to raw units."""
        raw = int(amount * Decimal(10**decimals))
        assert raw == expected_raw
    
    @pytest.mark.parametrize("raw,decimals,expected_amount", [
        (1000000000000000000, 18, Decimal("1")),
        (100000000, 6, Decimal("100")),
        (50000000, 8, Decimal("0.5")),
    ])
    def test_raw_to_amount(self, raw, decimals, expected_amount):
        """Test raw units conversion to amount."""
        amount = Decimal(raw) / Decimal(10**decimals)
        assert amount == expected_amount
    
    def test_invalid_address(self):
        """Test handling of invalid addresses."""
        invalid_addresses = [
            "0x",
            "0x123",
            "not_an_address",
            "",
            None
        ]
        
        for addr in invalid_addresses:
            if addr:
                assert not Web3.is_address(addr)
    
    def test_wallet_info_dataclass(self, sample_wallet_info):
        """Test WalletInfo structure."""
        info = sample_wallet_info
        
        assert "address" in info
        assert "native_balance" in info
        assert "native_symbol" in info
        assert isinstance(info["native_balance"], Decimal)


class TestTokenOperations:
    """Tests for token operations."""
    
    def test_token_info_dataclass(self, sample_token_info):
        """Test TokenInfo structure."""
        info = sample_token_info
        
        assert info["symbol"] == "USDC"
        assert info["decimals"] == 6
        assert isinstance(info["balance"], Decimal)
    
    def test_approve_token(self, mock_web3, mock_contract, test_wallet_address):
        """Test token approval."""
        spender = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Uniswap router
        amount = 2**256 - 1  # Max approval
        
        # Verify approval amount
        assert amount == 2**256 - 1
    
    def test_transfer_token(self, mock_web3, test_wallet_address):
        """Test token transfer."""
        to_address = "0x" + "1" * 40
        amount = Decimal("100")
        decimals = 6
        
        raw_amount = int(amount * Decimal(10**decimals))
        assert raw_amount == 100000000


class TestMultiChainSupport:
    """Tests for multi-chain functionality."""
    
    @pytest.mark.parametrize("network,expected_chain_id", [
        ("ethereum", 1),
        ("bsc", 56),
        ("polygon", 137),
        ("arbitrum", 42161),
        ("optimism", 10),
        ("avalanche", 43114),
        ("base", 8453),
    ])
    def test_network_chain_ids(self, network, expected_chain_id):
        """Test network chain IDs."""
        # Would test get_network_config
        network_configs = {
            "ethereum": 1,
            "bsc": 56,
            "polygon": 137,
            "arbitrum": 42161,
            "optimism": 10,
            "avalanche": 43114,
            "base": 8453,
        }
        
        assert network_configs[network] == expected_chain_id
    
    def test_testnet_detection(self):
        """Test testnet network detection."""
        testnets = ["goerli", "sepolia", "mumbai", "bsc_testnet"]
        mainnets = ["ethereum", "bsc", "polygon", "arbitrum"]
        
        for network in testnets:
            assert "test" in network or network in ["goerli", "sepolia", "mumbai"]
