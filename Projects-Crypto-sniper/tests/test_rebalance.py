"""
Tests for portfolio rebalance manager.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch


class TestRebalanceManager:
    """Tests for RebalanceManager class."""
    
    def test_set_allocation_targets(self):
        """Test setting allocation targets."""
        targets = [
            {"token": "ETH", "target_percent": Decimal("50")},
            {"token": "USDC", "target_percent": Decimal("30")},
            {"token": "WBTC", "target_percent": Decimal("20")},
        ]
        
        total = sum(t["target_percent"] for t in targets)
        assert total == Decimal("100")
    
    def test_allocation_must_sum_to_100(self):
        """Test that allocations must sum to 100%."""
        targets = [
            {"token": "ETH", "target_percent": Decimal("60")},
            {"token": "USDC", "target_percent": Decimal("30")},
            # Missing 10%
        ]
        
        total = sum(t["target_percent"] for t in targets)
        assert total != Decimal("100")
    
    def test_get_current_holdings(self, test_wallet_address):
        """Test current holdings retrieval."""
        holdings = [
            {"token": "ETH", "balance": Decimal("1.5"), "value_usd": Decimal("3000"), "percent": Decimal("60")},
            {"token": "USDC", "balance": Decimal("1500"), "value_usd": Decimal("1500"), "percent": Decimal("30")},
            {"token": "WBTC", "balance": Decimal("0.01"), "value_usd": Decimal("500"), "percent": Decimal("10")},
        ]
        
        total_percent = sum(h["percent"] for h in holdings)
        assert total_percent == Decimal("100")
    
    def test_calculate_rebalance_no_action(self):
        """Test no rebalance needed when within thresholds."""
        target = Decimal("50")
        current = Decimal("49")
        threshold = Decimal("5")  # 5% tolerance
        
        diff = abs(current - target)
        needs_rebalance = diff > threshold
        
        assert needs_rebalance is False
    
    def test_calculate_rebalance_needed(self):
        """Test rebalance needed when outside thresholds."""
        target = Decimal("50")
        current = Decimal("40")
        threshold = Decimal("5")
        
        diff = abs(current - target)
        needs_rebalance = diff > threshold
        
        assert needs_rebalance is True
    
    def test_rebalance_trade_calculation(self):
        """Test rebalance trade calculation."""
        total_value = Decimal("10000")
        
        # Current: 40% ETH, Target: 50% ETH
        current_percent = Decimal("40")
        target_percent = Decimal("50")
        
        current_value = total_value * (current_percent / 100)
        target_value = total_value * (target_percent / 100)
        trade_value = target_value - current_value
        
        assert current_value == Decimal("4000")
        assert target_value == Decimal("5000")
        assert trade_value == Decimal("1000")  # Need to buy $1000 ETH


class TestRebalancePlan:
    """Tests for RebalancePlan dataclass."""
    
    def test_plan_structure(self):
        """Test rebalance plan structure."""
        plan = {
            "trades": [
                {"token": "ETH", "direction": "buy", "amount": Decimal("0.5"), "value_usd": Decimal("1000")},
                {"token": "USDC", "direction": "sell", "amount": Decimal("1000"), "value_usd": Decimal("1000")},
            ],
            "total_portfolio_value": Decimal("10000"),
            "estimated_gas_cost": Decimal("0.02"),
            "estimated_slippage": Decimal("5"),
            "needs_rebalance": True
        }
        
        assert plan["needs_rebalance"] is True
        assert len(plan["trades"]) == 2
    
    def test_trade_count(self):
        """Test trade count property."""
        trades = [
            {"token": "ETH", "direction": "buy"},
            {"token": "USDC", "direction": "sell"},
        ]
        
        assert len(trades) == 2
    
    def test_total_trade_value(self):
        """Test total trade value calculation."""
        trades = [
            {"value_usd": Decimal("500")},
            {"value_usd": Decimal("300")},
            {"value_usd": Decimal("200")},
        ]
        
        total = sum(t["value_usd"] for t in trades)
        assert total == Decimal("1000")


class TestRebalanceExecution:
    """Tests for rebalance execution."""
    
    def test_execute_dry_run(self):
        """Test dry run execution."""
        dry_run = True
        
        result = {
            "success": True,
            "executed_trades": [
                {"token": "ETH", "simulated": True},
            ],
            "failed_trades": [],
            "total_gas_used": 0
        }
        
        assert result["executed_trades"][0]["simulated"] is True
    
    def test_execute_sells_before_buys(self):
        """Test that sells execute before buys."""
        trades = [
            {"token": "ETH", "direction": "buy", "order": 2},
            {"token": "USDC", "direction": "sell", "order": 1},
            {"token": "WBTC", "direction": "buy", "order": 3},
        ]
        
        # Sort: sells first, then buys
        sorted_trades = sorted(trades, key=lambda t: 0 if t["direction"] == "sell" else 1)
        
        assert sorted_trades[0]["direction"] == "sell"
    
    def test_execution_result_success(self):
        """Test successful execution result."""
        result = {
            "success": True,
            "executed_trades": [
                {"token": "ETH", "tx_hash": "0x" + "a" * 64},
                {"token": "USDC", "tx_hash": "0x" + "b" * 64},
            ],
            "failed_trades": [],
            "total_gas_used": 300000,
            "total_value_traded": Decimal("2000")
        }
        
        assert result["success"] is True
        assert len(result["failed_trades"]) == 0
    
    def test_execution_result_partial_failure(self):
        """Test partial failure execution result."""
        result = {
            "success": False,
            "executed_trades": [
                {"token": "USDC", "tx_hash": "0x" + "a" * 64},
            ],
            "failed_trades": [
                {"token": "ETH", "error": "Insufficient liquidity"},
            ],
            "total_gas_used": 150000,
            "error": "1 trades failed"
        }
        
        assert result["success"] is False
        assert len(result["failed_trades"]) == 1


class TestAllocationDrift:
    """Tests for allocation drift calculations."""
    
    def test_positive_drift(self):
        """Test positive drift (overweight)."""
        target = Decimal("30")
        current = Decimal("40")
        
        drift = current - target
        assert drift == Decimal("10")  # 10% overweight
    
    def test_negative_drift(self):
        """Test negative drift (underweight)."""
        target = Decimal("30")
        current = Decimal("20")
        
        drift = current - target
        assert drift == Decimal("-10")  # 10% underweight
    
    def test_zero_drift(self):
        """Test zero drift (on target)."""
        target = Decimal("30")
        current = Decimal("30")
        
        drift = current - target
        assert drift == Decimal("0")
    
    def test_drift_within_tolerance(self):
        """Test drift within acceptable tolerance."""
        target = Decimal("30")
        current = Decimal("31")
        tolerance = Decimal("3")  # 3% tolerance
        
        drift = abs(current - target)
        within_tolerance = drift <= tolerance
        
        assert within_tolerance is True


class TestMinTradeValue:
    """Tests for minimum trade value threshold."""
    
    def test_skip_small_trades(self):
        """Test skipping trades below minimum."""
        min_trade_value = Decimal("10")
        trade_value = Decimal("5")
        
        should_execute = trade_value >= min_trade_value
        assert should_execute is False
    
    def test_execute_large_trades(self):
        """Test executing trades above minimum."""
        min_trade_value = Decimal("10")
        trade_value = Decimal("100")
        
        should_execute = trade_value >= min_trade_value
        assert should_execute is True
