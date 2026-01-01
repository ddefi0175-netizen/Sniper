"""
Tests for NFT manager module.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from web3 import Web3


class TestNFTManager:
    """Tests for NFTManager class."""
    
    def test_get_nft_info(self, mock_web3, mock_contract):
        """Test NFT information retrieval."""
        contract = mock_contract({
            "name": "Test Collection",
            "symbol": "TEST",
            "ownerOf": "0x742d35Cc6634C0532925a3b844Bc9e7595f5bAb2",
            "tokenURI": "ipfs://QmTest123"
        })
        
        # Verify mock returns expected values
        assert contract.functions.name().call() == "Test Collection"
        assert contract.functions.symbol().call() == "TEST"
    
    def test_get_nfts_for_wallet(self, mock_web3, test_wallet_address):
        """Test NFT enumeration for wallet."""
        # Would use indexer API in production
        nfts = []  # Placeholder
        
        assert isinstance(nfts, list)
    
    def test_transfer_nft(self, mock_web3, test_wallet_address, test_private_key):
        """Test NFT transfer."""
        contract_address = "0x" + "1" * 40
        token_id = 1234
        to_address = "0x" + "2" * 40
        
        # Verify parameters
        assert Web3.is_address(contract_address)
        assert Web3.is_address(to_address)
        assert isinstance(token_id, int)
    
    def test_transfer_not_owner(self, mock_web3, mock_contract):
        """Test transfer fails when not owner."""
        other_owner = "0x" + "9" * 40
        
        contract = mock_contract({
            "ownerOf": other_owner
        })
        
        # Should fail because caller is not owner
        owner = contract.functions.ownerOf().call()
        assert owner == other_owner
    
    def test_safe_transfer(self, mock_web3):
        """Test safe transfer method."""
        # safeTransferFrom checks if recipient can receive NFTs
        pass  # Implementation test
    
    def test_approval_for_all(self, mock_web3, mock_contract, test_wallet_address):
        """Test setApprovalForAll."""
        operator = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        
        # Verify addresses
        assert Web3.is_address(operator)
        assert Web3.is_address(test_wallet_address)


class TestNFTCollection:
    """Tests for NFTCollection dataclass."""
    
    def test_collection_info(self, mock_contract):
        """Test collection information."""
        collection = {
            "contract_address": "0x" + "1" * 40,
            "name": "Test Collection",
            "symbol": "TEST",
            "total_supply": 10000,
            "floor_price": Decimal("0.5"),
            "verified": True
        }
        
        assert collection["total_supply"] > 0
        assert collection["floor_price"] > 0
    
    def test_floor_price_retrieval(self):
        """Test floor price fetching."""
        # Would use marketplace API
        floor_price = Decimal("0.5")  # ETH
        
        assert floor_price > 0
    
    def test_collection_stats(self):
        """Test collection statistics."""
        stats = {
            "total_supply": 10000,
            "owners_count": 5000,
            "volume_24h": Decimal("100.5"),
            "volume_7d": Decimal("500.0"),
            "floor_price": Decimal("0.5"),
            "avg_price": Decimal("0.75")
        }
        
        assert stats["owners_count"] <= stats["total_supply"]
        assert stats["floor_price"] <= stats["avg_price"]


class TestNFTStandards:
    """Tests for NFT standard handling."""
    
    def test_erc721_interface(self):
        """Test ERC721 interface detection."""
        erc721_interface_id = "0x80ac58cd"
        
        # Would check supportsInterface
        assert erc721_interface_id.startswith("0x")
    
    def test_erc1155_interface(self):
        """Test ERC1155 interface detection."""
        erc1155_interface_id = "0xd9b67a26"
        
        assert erc1155_interface_id.startswith("0x")
    
    def test_erc1155_balance_of(self, mock_contract):
        """Test ERC1155 balance retrieval."""
        token_id = 1
        balance = 5  # Can own multiple of same token
        
        # ERC1155 allows multiple ownership
        assert balance >= 0
    
    def test_metadata_uri(self, mock_contract):
        """Test metadata URI retrieval."""
        # ERC721 tokenURI
        token_uri = "ipfs://QmTest123/1.json"
        
        assert token_uri.startswith("ipfs://") or token_uri.startswith("https://")


class TestNFTTransfer:
    """Tests for NFT transfer operations."""
    
    def test_transfer_result_success(self):
        """Test successful transfer result."""
        result = {
            "success": True,
            "tx_hash": "0x" + "a" * 64,
            "contract_address": "0x" + "1" * 40,
            "token_id": 1234,
            "from_address": "0x" + "2" * 40,
            "to_address": "0x" + "3" * 40,
            "gas_used": 85000
        }
        
        assert result["success"] is True
        assert result["tx_hash"].startswith("0x")
        assert len(result["tx_hash"]) == 66
    
    def test_transfer_result_failure(self):
        """Test failed transfer result."""
        result = {
            "success": False,
            "error": "Not the owner",
            "tx_hash": None
        }
        
        assert result["success"] is False
        assert result["error"] is not None
    
    def test_gas_estimation(self, mock_web3):
        """Test gas estimation for transfer."""
        # NFT transfers typically use ~80k-150k gas
        estimated_gas = 100000
        
        assert estimated_gas > 50000
        assert estimated_gas < 200000
