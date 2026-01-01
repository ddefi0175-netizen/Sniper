"""
NFT Manager - ERC721 and ERC1155 token management.

Provides functionality for NFT discovery, transfer, and marketplace integration.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from web3 import Web3

logger = logging.getLogger(__name__)


# Standard ERC721 ABI (minimal)
ERC721_ABI = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "tokenId", "type": "uint256"}], "name": "ownerOf", "outputs": [{"name": "", "type": "address"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "tokenId", "type": "uint256"}], "name": "tokenURI", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}, {"name": "tokenId", "type": "uint256"}], "name": "transferFrom", "outputs": [], "type": "function"},
    {"constant": False, "inputs": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}, {"name": "tokenId", "type": "uint256"}], "name": "safeTransferFrom", "outputs": [], "type": "function"},
    {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "approved", "type": "bool"}], "name": "setApprovalForAll", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "operator", "type": "address"}], "name": "isApprovedForAll", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
]

# Standard ERC1155 ABI (minimal)
ERC1155_ABI = [
    {"constant": True, "inputs": [{"name": "account", "type": "address"}, {"name": "id", "type": "uint256"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "id", "type": "uint256"}], "name": "uri", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"}, {"name": "id", "type": "uint256"}, {"name": "amount", "type": "uint256"}, {"name": "data", "type": "bytes"}], "name": "safeTransferFrom", "outputs": [], "type": "function"},
]


class NFTStandard(Enum):
    """NFT token standard."""
    ERC721 = "erc721"
    ERC1155 = "erc1155"


@dataclass
class NFTInfo:
    """Information about a single NFT."""
    
    contract_address: str
    token_id: int
    standard: NFTStandard
    name: str
    symbol: str
    token_uri: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    owner: Optional[str] = None
    amount: int = 1  # For ERC1155
    
    # Market data
    floor_price: Optional[Decimal] = None
    last_sale_price: Optional[Decimal] = None
    estimated_value: Optional[Decimal] = None


@dataclass
class NFTCollection:
    """Information about an NFT collection."""
    
    contract_address: str
    name: str
    symbol: str
    standard: NFTStandard
    total_supply: Optional[int] = None
    floor_price: Optional[Decimal] = None
    volume_24h: Optional[Decimal] = None
    owners_count: Optional[int] = None
    verified: bool = False
    image_url: Optional[str] = None
    description: Optional[str] = None


@dataclass
class NFTTransferResult:
    """Result of NFT transfer operation."""
    
    success: bool
    tx_hash: Optional[str] = None
    contract_address: Optional[str] = None
    token_id: Optional[int] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    gas_used: Optional[int] = None
    error: Optional[str] = None


class NFTManager:
    """
    Manager for NFT operations.
    
    Supports ERC721 and ERC1155 tokens with features for:
    - NFT discovery and enumeration
    - Metadata retrieval
    - Safe transfers
    - Collection floor prices
    
    Example:
        manager = NFTManager(network="ethereum")
        
        # Get all NFTs for an address
        nfts = manager.get_nfts("0x...")
        
        # Transfer an NFT
        result = manager.transfer_nft(
            contract_address="0x...",
            token_id=1234,
            to_address="0x...",
            private_key="0x..."
        )
        
        # Get collection info
        collection = manager.get_collection("0x...")
        print(f"Floor: {collection.floor_price} ETH")
    """
    
    def __init__(
        self,
        network: str = "ethereum",
        private_key: Optional[str] = None
    ):
        """
        Initialize NFT manager.
        
        Args:
            network: Network name
            private_key: Private key for write operations
        """
        self.network = network
        self.private_key = private_key
        self._web3: Optional[Web3] = None
        self._collections_cache: Dict[str, NFTCollection] = {}
    
    def _get_web3(self) -> Web3:
        """Get or create Web3 instance."""
        if self._web3 is None:
            # In production, use proper RPC from config
            from config.networks import get_network_config
            config = get_network_config(self.network)
            self._web3 = Web3(Web3.HTTPProvider(config.rpc_url))
        return self._web3
    
    def get_nfts(
        self,
        address: str,
        collections: Optional[List[str]] = None
    ) -> List[NFTInfo]:
        """
        Get all NFTs owned by an address.
        
        Args:
            address: Wallet address
            collections: Optional list of collection addresses to filter
        
        Returns:
            List of NFT information
        
        Note:
            In production, this would use an indexer API like Alchemy NFT API
            or OpenSea API for efficient NFT enumeration.
        """
        address = Web3.to_checksum_address(address)
        nfts = []
        
        # This is a placeholder - in production use NFT indexer API
        logger.info(f"Fetching NFTs for {address}")
        
        if collections:
            for collection_address in collections:
                try:
                    collection_nfts = self._get_nfts_from_collection(
                        address, collection_address
                    )
                    nfts.extend(collection_nfts)
                except Exception as e:
                    logger.warning(f"Error fetching from {collection_address}: {e}")
        
        return nfts
    
    def _get_nfts_from_collection(
        self,
        owner: str,
        collection_address: str
    ) -> List[NFTInfo]:
        """Get NFTs from a specific collection."""
        web3 = self._get_web3()
        collection_address = Web3.to_checksum_address(collection_address)
        
        try:
            contract = web3.eth.contract(
                address=collection_address,
                abi=ERC721_ABI
            )
            
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            balance = contract.functions.balanceOf(owner).call()
            
            nfts = []
            # Note: This requires enumerable extension or indexer
            # Placeholder for demonstration
            
            return nfts
            
        except Exception as e:
            logger.error(f"Error reading collection {collection_address}: {e}")
            return []
    
    def get_nft(
        self,
        contract_address: str,
        token_id: int
    ) -> Optional[NFTInfo]:
        """
        Get information about a specific NFT.
        
        Args:
            contract_address: NFT contract address
            token_id: Token ID
        
        Returns:
            NFT information or None
        """
        web3 = self._get_web3()
        contract_address = Web3.to_checksum_address(contract_address)
        
        try:
            contract = web3.eth.contract(
                address=contract_address,
                abi=ERC721_ABI
            )
            
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            owner = contract.functions.ownerOf(token_id).call()
            
            try:
                token_uri = contract.functions.tokenURI(token_id).call()
            except Exception:
                token_uri = None
            
            return NFTInfo(
                contract_address=contract_address,
                token_id=token_id,
                standard=NFTStandard.ERC721,
                name=name,
                symbol=symbol,
                token_uri=token_uri,
                owner=owner
            )
            
        except Exception as e:
            logger.error(f"Error fetching NFT {contract_address}#{token_id}: {e}")
            return None
    
    def transfer_nft(
        self,
        contract_address: str,
        token_id: int,
        to_address: str,
        private_key: Optional[str] = None,
        use_safe_transfer: bool = True
    ) -> NFTTransferResult:
        """
        Transfer an NFT to another address.
        
        Args:
            contract_address: NFT contract address
            token_id: Token ID to transfer
            to_address: Recipient address
            private_key: Sender's private key (or use instance default)
            use_safe_transfer: Use safeTransferFrom (recommended)
        
        Returns:
            Transfer result
        """
        key = private_key or self.private_key
        if not key:
            return NFTTransferResult(
                success=False,
                error="No private key provided"
            )
        
        web3 = self._get_web3()
        contract_address = Web3.to_checksum_address(contract_address)
        to_address = Web3.to_checksum_address(to_address)
        
        try:
            account = web3.eth.account.from_key(key)
            from_address = account.address
            
            contract = web3.eth.contract(
                address=contract_address,
                abi=ERC721_ABI
            )
            
            # Verify ownership
            owner = contract.functions.ownerOf(token_id).call()
            if owner.lower() != from_address.lower():
                return NFTTransferResult(
                    success=False,
                    error=f"Not the owner. Owner is {owner}"
                )
            
            # Build transaction
            if use_safe_transfer:
                tx = contract.functions.safeTransferFrom(
                    from_address, to_address, token_id
                )
            else:
                tx = contract.functions.transferFrom(
                    from_address, to_address, token_id
                )
            
            # Estimate gas
            gas_estimate = tx.estimate_gas({'from': from_address})
            gas_price = web3.eth.gas_price
            
            # Build and sign transaction
            tx_dict = tx.build_transaction({
                'from': from_address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': gas_price,
                'nonce': web3.eth.get_transaction_count(from_address),
            })
            
            signed = account.sign_transaction(tx_dict)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            
            # Wait for receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return NFTTransferResult(
                success=receipt['status'] == 1,
                tx_hash=tx_hash.hex(),
                contract_address=contract_address,
                token_id=token_id,
                from_address=from_address,
                to_address=to_address,
                gas_used=receipt['gasUsed']
            )
            
        except Exception as e:
            logger.error(f"NFT transfer failed: {e}")
            return NFTTransferResult(
                success=False,
                error=str(e)
            )
    
    def get_collection(self, contract_address: str) -> Optional[NFTCollection]:
        """
        Get collection information.
        
        Args:
            contract_address: Collection contract address
        
        Returns:
            Collection information
        """
        contract_address = Web3.to_checksum_address(contract_address)
        
        # Check cache
        if contract_address in self._collections_cache:
            return self._collections_cache[contract_address]
        
        web3 = self._get_web3()
        
        try:
            contract = web3.eth.contract(
                address=contract_address,
                abi=ERC721_ABI
            )
            
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            
            collection = NFTCollection(
                contract_address=contract_address,
                name=name,
                symbol=symbol,
                standard=NFTStandard.ERC721
            )
            
            self._collections_cache[contract_address] = collection
            return collection
            
        except Exception as e:
            logger.error(f"Error fetching collection {contract_address}: {e}")
            return None
    
    def get_floor_price(
        self,
        contract_address: str
    ) -> Optional[Decimal]:
        """
        Get floor price for a collection.
        
        Args:
            contract_address: Collection contract address
        
        Returns:
            Floor price in ETH or None
        
        Note:
            In production, integrate with OpenSea, LooksRare, or Reservoir API
        """
        # Placeholder - would use marketplace API
        logger.info(f"Getting floor price for {contract_address}")
        return None
    
    def set_approval_for_all(
        self,
        contract_address: str,
        operator: str,
        approved: bool,
        private_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set approval for an operator to manage all NFTs.
        
        Args:
            contract_address: NFT contract address
            operator: Operator address (marketplace, etc.)
            approved: Whether to approve or revoke
            private_key: Owner's private key
        
        Returns:
            Transaction result
        """
        key = private_key or self.private_key
        if not key:
            return {"success": False, "error": "No private key provided"}
        
        web3 = self._get_web3()
        contract_address = Web3.to_checksum_address(contract_address)
        operator = Web3.to_checksum_address(operator)
        
        try:
            account = web3.eth.account.from_key(key)
            
            contract = web3.eth.contract(
                address=contract_address,
                abi=ERC721_ABI
            )
            
            tx = contract.functions.setApprovalForAll(operator, approved)
            
            gas_estimate = tx.estimate_gas({'from': account.address})
            
            tx_dict = tx.build_transaction({
                'from': account.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(account.address),
            })
            
            signed = account.sign_transaction(tx_dict)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "success": receipt['status'] == 1,
                "tx_hash": tx_hash.hex(),
                "operator": operator,
                "approved": approved
            }
            
        except Exception as e:
            logger.error(f"setApprovalForAll failed: {e}")
            return {"success": False, "error": str(e)}
    
    def is_approved_for_all(
        self,
        contract_address: str,
        owner: str,
        operator: str
    ) -> bool:
        """Check if operator is approved for all NFTs."""
        web3 = self._get_web3()
        contract_address = Web3.to_checksum_address(contract_address)
        owner = Web3.to_checksum_address(owner)
        operator = Web3.to_checksum_address(operator)
        
        try:
            contract = web3.eth.contract(
                address=contract_address,
                abi=ERC721_ABI
            )
            
            return contract.functions.isApprovedForAll(owner, operator).call()
            
        except Exception as e:
            logger.error(f"isApprovedForAll check failed: {e}")
            return False
