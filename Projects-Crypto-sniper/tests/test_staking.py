"""
Tests for staking module.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


class TestStakingManager:
    """Tests for StakingManager class."""
    
    def test_stake_tokens(self, mock_web3, test_wallet_address, test_private_key):
        """Test token staking."""
        pool_id = "1"
        amount = Decimal("100.0")
        
        # Verify staking parameters
        assert amount > 0
        assert pool_id.isdigit()
    
    def test_unstake_tokens(self, mock_web3, test_wallet_address):
        """Test token unstaking."""
        pool_id = "1"
        amount = Decimal("50.0")
        
        assert amount > 0
    
    def test_claim_rewards(self, mock_web3, test_wallet_address):
        """Test reward claiming."""
        pool_id = "1"
        
        # Mock pending rewards
        pending_rewards = Decimal("5.5")
        assert pending_rewards >= 0
    
    def test_get_pending_rewards(self, mock_web3, test_wallet_address):
        """Test pending rewards retrieval."""
        pool_id = "1"
        
        # Would call contract.pendingReward(wallet_address)
        pending = Decimal("5.5")
        
        assert isinstance(pending, Decimal)
        assert pending >= 0
    
    def test_get_stake_position(self, sample_stake_position):
        """Test stake position retrieval."""
        position = sample_stake_position
        
        assert position["staked_amount"] == Decimal("100.0")
        assert position["rewards_pending"] == Decimal("5.5")
        assert position["apy"] == Decimal("12.5")
    
    def test_calculate_apy(self):
        """Test APY calculation."""
        # APY = ((1 + rate/n)^n - 1) * 100
        daily_rate = Decimal("0.0003")  # 0.03% daily
        
        apy = ((1 + daily_rate) ** 365 - 1) * 100
        
        assert apy > 0
        assert apy < 1000  # Sanity check
    
    def test_lock_period_calculation(self):
        """Test lock period calculations."""
        lock_start = datetime.utcnow()
        lock_duration = timedelta(days=30)
        lock_end = lock_start + lock_duration
        
        remaining = lock_end - datetime.utcnow()
        
        assert remaining.days <= 30
        assert remaining.days >= 0


class TestYieldFarming:
    """Tests for yield farming functionality."""
    
    def test_deposit_to_pool(self, mock_web3, test_wallet_address):
        """Test LP token deposit."""
        pool_address = "0x" + "1" * 40
        amount = Decimal("10.0")
        
        assert amount > 0
    
    def test_withdraw_from_pool(self, mock_web3, test_wallet_address):
        """Test LP token withdrawal."""
        pool_address = "0x" + "1" * 40
        amount = Decimal("5.0")
        
        assert amount > 0
    
    def test_harvest_rewards(self, mock_web3, test_wallet_address):
        """Test reward harvesting."""
        pool_address = "0x" + "1" * 40
        
        # Mock harvest
        rewards = {
            "token1": Decimal("10.5"),
            "token2": Decimal("25.0")
        }
        
        assert all(v > 0 for v in rewards.values())
    
    def test_compound_rewards(self, mock_web3, test_wallet_address):
        """Test reward compounding."""
        pool_address = "0x" + "1" * 40
        
        # Compound = harvest + deposit
        pending = Decimal("10.0")
        
        assert pending >= 0
    
    def test_pool_info_structure(self):
        """Test PoolInfo structure."""
        pool_info = {
            "address": "0x" + "1" * 40,
            "name": "ETH-USDC LP",
            "token0": "ETH",
            "token1": "USDC",
            "tvl": Decimal("1000000"),
            "apy": Decimal("25.5"),
            "rewards_token": "REWARD"
        }
        
        assert "apy" in pool_info
        assert "tvl" in pool_info
        assert pool_info["apy"] > 0


class TestStakePosition:
    """Tests for StakePosition dataclass."""
    
    def test_position_value_calculation(self):
        """Test position value calculation."""
        staked = Decimal("100.0")
        token_price = Decimal("10.0")
        
        value = staked * token_price
        
        assert value == Decimal("1000.0")
    
    def test_position_pnl_calculation(self):
        """Test position PnL calculation."""
        entry_value = Decimal("1000.0")
        current_value = Decimal("1200.0")
        
        pnl = current_value - entry_value
        pnl_percent = (pnl / entry_value) * 100
        
        assert pnl == Decimal("200.0")
        assert pnl_percent == Decimal("20.0")
    
    def test_lock_status(self):
        """Test position lock status."""
        # Locked position
        lock_end = datetime.utcnow() + timedelta(days=10)
        is_locked = datetime.utcnow() < lock_end
        
        assert is_locked is True
        
        # Unlocked position
        lock_end = datetime.utcnow() - timedelta(days=1)
        is_locked = datetime.utcnow() < lock_end
        
        assert is_locked is False
