"""
Multi-signature wallet manager.

Provides secure multi-party transaction approval for high-value operations.
"""

import logging
import time
import hashlib
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal

from web3 import Web3
from eth_account.messages import encode_defunct

logger = logging.getLogger(__name__)


class ProposalStatus(Enum):
    """Status of a multi-sig proposal."""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class MultiSigProposal:
    """A multi-signature transaction proposal."""
    
    proposal_id: str
    creator: str
    description: str
    target_address: str
    value: Decimal
    calldata: bytes
    signatures: Dict[str, str] = field(default_factory=dict)
    required_signatures: int = 2
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0
    status: ProposalStatus = ProposalStatus.PENDING
    executed_tx_hash: Optional[str] = None
    
    def __post_init__(self):
        if self.expires_at == 0:
            self.expires_at = self.created_at + 86400 * 7  # 7 days default
    
    @property
    def signature_count(self) -> int:
        """Get number of signatures collected."""
        return len(self.signatures)
    
    @property
    def is_ready(self) -> bool:
        """Check if proposal has enough signatures."""
        return self.signature_count >= self.required_signatures
    
    @property
    def is_expired(self) -> bool:
        """Check if proposal has expired."""
        return time.time() > self.expires_at
    
    def get_message_hash(self) -> bytes:
        """Get the message hash for signing."""
        message = f"{self.proposal_id}:{self.target_address}:{self.value}:{self.calldata.hex()}"
        return hashlib.sha256(message.encode()).digest()


@dataclass
class MultiSigWallet:
    """Configuration for a multi-sig wallet."""
    
    wallet_id: str
    name: str
    owners: List[str]
    required_signatures: int
    created_at: float = field(default_factory=time.time)
    proposals: Dict[str, MultiSigProposal] = field(default_factory=dict)


class MultiSigManager:
    """
    Manager for multi-signature wallet operations.
    
    Enables secure multi-party approval for transactions,
    ideal for treasury management and high-value operations.
    
    Example:
        manager = MultiSigManager()
        
        # Create a multi-sig wallet
        wallet = manager.create_wallet(
            name="Treasury",
            owners=["0x...", "0x...", "0x..."],
            required_signatures=2
        )
        
        # Create a proposal
        proposal = manager.create_proposal(
            wallet_id=wallet.wallet_id,
            creator="0x...",
            description="Transfer 10 ETH to marketing",
            target_address="0x...",
            value=Decimal("10"),
            calldata=b""
        )
        
        # Sign the proposal
        manager.sign_proposal(
            wallet_id=wallet.wallet_id,
            proposal_id=proposal.proposal_id,
            signer="0x...",
            signature="0x..."
        )
        
        # Execute when ready
        if proposal.is_ready:
            tx_hash = manager.execute_proposal(
                wallet_id=wallet.wallet_id,
                proposal_id=proposal.proposal_id
            )
    """
    
    def __init__(self, network: str = "ethereum"):
        """
        Initialize multi-sig manager.
        
        Args:
            network: Network name
        """
        self.network = network
        self._wallets: Dict[str, MultiSigWallet] = {}
        self._proposal_counter = 0
    
    def create_wallet(
        self,
        name: str,
        owners: List[str],
        required_signatures: int
    ) -> MultiSigWallet:
        """
        Create a new multi-sig wallet configuration.
        
        Args:
            name: Wallet name
            owners: List of owner addresses
            required_signatures: Number of signatures required
        
        Returns:
            Created MultiSigWallet
        
        Raises:
            ValueError: If configuration is invalid
        """
        if required_signatures > len(owners):
            raise ValueError("Required signatures cannot exceed number of owners")
        
        if required_signatures < 1:
            raise ValueError("At least 1 signature required")
        
        # Validate and checksum addresses
        validated_owners = []
        for owner in owners:
            if not Web3.is_address(owner):
                raise ValueError(f"Invalid owner address: {owner}")
            validated_owners.append(Web3.to_checksum_address(owner))
        
        wallet_id = hashlib.sha256(
            f"{name}:{','.join(validated_owners)}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        wallet = MultiSigWallet(
            wallet_id=wallet_id,
            name=name,
            owners=validated_owners,
            required_signatures=required_signatures
        )
        
        self._wallets[wallet_id] = wallet
        logger.info(f"Created multi-sig wallet: {name} ({wallet_id})")
        
        return wallet
    
    def get_wallet(self, wallet_id: str) -> Optional[MultiSigWallet]:
        """Get wallet by ID."""
        return self._wallets.get(wallet_id)
    
    def create_proposal(
        self,
        wallet_id: str,
        creator: str,
        description: str,
        target_address: str,
        value: Decimal,
        calldata: bytes = b"",
        expires_in_days: int = 7
    ) -> MultiSigProposal:
        """
        Create a new transaction proposal.
        
        Args:
            wallet_id: Multi-sig wallet ID
            creator: Address of proposal creator
            description: Human-readable description
            target_address: Transaction target
            value: ETH value to send
            calldata: Transaction data
            expires_in_days: Expiration time
        
        Returns:
            Created proposal
        
        Raises:
            ValueError: If wallet not found or creator not an owner
        """
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        creator = Web3.to_checksum_address(creator)
        if creator not in wallet.owners:
            raise ValueError(f"Creator {creator} is not a wallet owner")
        
        if not Web3.is_address(target_address):
            raise ValueError(f"Invalid target address: {target_address}")
        
        self._proposal_counter += 1
        proposal_id = f"prop-{wallet_id[:8]}-{self._proposal_counter}"
        
        proposal = MultiSigProposal(
            proposal_id=proposal_id,
            creator=creator,
            description=description,
            target_address=Web3.to_checksum_address(target_address),
            value=value,
            calldata=calldata,
            required_signatures=wallet.required_signatures,
            expires_at=time.time() + (expires_in_days * 86400)
        )
        
        wallet.proposals[proposal_id] = proposal
        logger.info(f"Created proposal: {proposal_id} - {description}")
        
        return proposal
    
    def sign_proposal(
        self,
        wallet_id: str,
        proposal_id: str,
        signer: str,
        signature: str
    ) -> MultiSigProposal:
        """
        Add a signature to a proposal.
        
        Args:
            wallet_id: Multi-sig wallet ID
            proposal_id: Proposal ID
            signer: Signer address
            signature: Signature hex string
        
        Returns:
            Updated proposal
        
        Raises:
            ValueError: If validation fails
        """
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        proposal = wallet.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(f"Proposal is not pending: {proposal.status.value}")
        
        if proposal.is_expired:
            proposal.status = ProposalStatus.EXPIRED
            raise ValueError("Proposal has expired")
        
        signer = Web3.to_checksum_address(signer)
        if signer not in wallet.owners:
            raise ValueError(f"Signer {signer} is not a wallet owner")
        
        if signer in proposal.signatures:
            raise ValueError(f"Signer {signer} has already signed")
        
        # Verify signature
        message_hash = proposal.get_message_hash()
        message = encode_defunct(primitive=message_hash)
        
        try:
            recovered = Web3().eth.account.recover_message(message, signature=signature)
            if recovered.lower() != signer.lower():
                raise ValueError("Signature verification failed")
        except Exception as e:
            raise ValueError(f"Invalid signature: {e}")
        
        proposal.signatures[signer] = signature
        logger.info(f"Signature added to {proposal_id} by {signer}")
        
        # Check if ready for execution
        if proposal.is_ready:
            proposal.status = ProposalStatus.APPROVED
            logger.info(f"Proposal {proposal_id} approved with {proposal.signature_count} signatures")
        
        return proposal
    
    def execute_proposal(
        self,
        wallet_id: str,
        proposal_id: str,
        executor_private_key: str
    ) -> Dict[str, Any]:
        """
        Execute an approved proposal.
        
        Args:
            wallet_id: Multi-sig wallet ID
            proposal_id: Proposal ID
            executor_private_key: Private key for gas payment
        
        Returns:
            Execution result with tx_hash
        
        Raises:
            ValueError: If proposal not ready
        """
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        proposal = wallet.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        if proposal.status == ProposalStatus.EXECUTED:
            raise ValueError("Proposal already executed")
        
        if proposal.status != ProposalStatus.APPROVED:
            if not proposal.is_ready:
                raise ValueError(
                    f"Not enough signatures: {proposal.signature_count}/{proposal.required_signatures}"
                )
            proposal.status = ProposalStatus.APPROVED
        
        if proposal.is_expired:
            proposal.status = ProposalStatus.EXPIRED
            raise ValueError("Proposal has expired")
        
        # In production, this would execute the actual transaction
        # For now, simulate execution
        logger.info(f"Executing proposal {proposal_id}")
        logger.info(f"  Target: {proposal.target_address}")
        logger.info(f"  Value: {proposal.value} ETH")
        logger.info(f"  Signatures: {list(proposal.signatures.keys())}")
        
        # Simulate tx hash
        tx_hash = Web3.keccak(
            text=f"{proposal_id}:{time.time()}"
        ).hex()
        
        proposal.status = ProposalStatus.EXECUTED
        proposal.executed_tx_hash = tx_hash
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "proposal_id": proposal_id,
            "value": str(proposal.value),
            "target": proposal.target_address
        }
    
    def reject_proposal(
        self,
        wallet_id: str,
        proposal_id: str,
        rejector: str
    ) -> MultiSigProposal:
        """
        Reject a proposal.
        
        Args:
            wallet_id: Multi-sig wallet ID
            proposal_id: Proposal ID
            rejector: Address of rejector (must be owner)
        
        Returns:
            Updated proposal
        """
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            raise ValueError(f"Wallet not found: {wallet_id}")
        
        proposal = wallet.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        rejector = Web3.to_checksum_address(rejector)
        if rejector not in wallet.owners:
            raise ValueError(f"Rejector {rejector} is not a wallet owner")
        
        proposal.status = ProposalStatus.REJECTED
        logger.info(f"Proposal {proposal_id} rejected by {rejector}")
        
        return proposal
    
    def get_pending_proposals(self, wallet_id: str) -> List[MultiSigProposal]:
        """Get all pending proposals for a wallet."""
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            return []
        
        pending = []
        for proposal in wallet.proposals.values():
            if proposal.is_expired and proposal.status == ProposalStatus.PENDING:
                proposal.status = ProposalStatus.EXPIRED
            
            if proposal.status == ProposalStatus.PENDING:
                pending.append(proposal)
        
        return pending
    
    def get_proposal_history(
        self,
        wallet_id: str,
        limit: int = 50
    ) -> List[MultiSigProposal]:
        """Get proposal history for a wallet."""
        wallet = self._wallets.get(wallet_id)
        if not wallet:
            return []
        
        proposals = sorted(
            wallet.proposals.values(),
            key=lambda p: p.created_at,
            reverse=True
        )
        
        return proposals[:limit]
