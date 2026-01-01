"""
Portfolio Rebalance Manager.

Provides automated portfolio rebalancing to maintain target allocations.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from web3 import Web3

logger = logging.getLogger(__name__)


class TradeDirection(Enum):
    """Direction of rebalance trade."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class AllocationTarget:
    """Target allocation for an asset."""
    
    token_address: str
    symbol: str
    target_percent: Decimal  # 0-100
    min_percent: Optional[Decimal] = None  # Trigger rebalance below this
    max_percent: Optional[Decimal] = None  # Trigger rebalance above this
    
    def __post_init__(self):
        if self.min_percent is None:
            self.min_percent = self.target_percent * Decimal("0.9")
        if self.max_percent is None:
            self.max_percent = self.target_percent * Decimal("1.1")


@dataclass
class CurrentHolding:
    """Current holding of an asset."""
    
    token_address: str
    symbol: str
    balance: Decimal
    value_usd: Decimal
    current_percent: Decimal


@dataclass
class RebalanceTrade:
    """A single trade in a rebalance plan."""
    
    token_address: str
    symbol: str
    direction: TradeDirection
    amount: Decimal
    value_usd: Decimal
    from_percent: Decimal
    to_percent: Decimal


@dataclass
class RebalancePlan:
    """Complete rebalance plan."""
    
    trades: List[RebalanceTrade]
    total_portfolio_value: Decimal
    estimated_gas_cost: Decimal
    estimated_slippage: Decimal
    needs_rebalance: bool
    
    @property
    def trade_count(self) -> int:
        return len(self.trades)
    
    @property
    def total_trade_value(self) -> Decimal:
        return sum(t.value_usd for t in self.trades)


@dataclass
class RebalanceResult:
    """Result of rebalance execution."""
    
    success: bool
    executed_trades: List[Dict[str, Any]]
    failed_trades: List[Dict[str, Any]]
    total_gas_used: int
    total_value_traded: Decimal
    error: Optional[str] = None


class RebalanceManager:
    """
    Portfolio rebalance manager.
    
    Automatically calculates and executes trades to maintain
    target portfolio allocations.
    
    Example:
        manager = RebalanceManager(network="ethereum")
        
        # Set target allocations
        manager.set_target_allocation([
            AllocationTarget("0x...", "ETH", Decimal("50")),
            AllocationTarget("0x...", "USDC", Decimal("30")),
            AllocationTarget("0x...", "WBTC", Decimal("20")),
        ])
        
        # Check if rebalance needed
        plan = manager.calculate_rebalance_trades("0xMyWallet...")
        
        if plan.needs_rebalance:
            print(f"Need to execute {plan.trade_count} trades")
            result = manager.execute_rebalance(plan, private_key="0x...")
    """
    
    # Native token placeholder address
    NATIVE_TOKEN = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    
    def __init__(
        self,
        network: str = "ethereum",
        dex_router: Optional[str] = None,
        slippage_tolerance: Decimal = Decimal("0.5"),
        min_trade_value_usd: Decimal = Decimal("10")
    ):
        """
        Initialize rebalance manager.
        
        Args:
            network: Network name
            dex_router: DEX router address for swaps
            slippage_tolerance: Max slippage percent
            min_trade_value_usd: Minimum trade value to execute
        """
        self.network = network
        self.dex_router = dex_router
        self.slippage_tolerance = slippage_tolerance
        self.min_trade_value_usd = min_trade_value_usd
        
        self._targets: List[AllocationTarget] = []
        self._web3: Optional[Web3] = None
    
    def _get_web3(self) -> Web3:
        """Get or create Web3 instance."""
        if self._web3 is None:
            from config.networks import get_network_config
            config = get_network_config(self.network)
            self._web3 = Web3(Web3.HTTPProvider(config.rpc_url))
        return self._web3
    
    def set_target_allocation(self, targets: List[AllocationTarget]) -> None:
        """
        Set target portfolio allocations.
        
        Args:
            targets: List of allocation targets
        
        Raises:
            ValueError: If allocations don't sum to 100%
        """
        total = sum(t.target_percent for t in targets)
        
        if total != Decimal("100"):
            raise ValueError(f"Allocations must sum to 100%, got {total}%")
        
        # Validate addresses
        for target in targets:
            if target.token_address != self.NATIVE_TOKEN:
                if not Web3.is_address(target.token_address):
                    raise ValueError(f"Invalid token address: {target.token_address}")
        
        self._targets = targets
        logger.info(f"Set {len(targets)} allocation targets")
    
    def get_target_allocation(self) -> List[AllocationTarget]:
        """Get current target allocations."""
        return self._targets.copy()
    
    def get_current_holdings(
        self,
        wallet_address: str
    ) -> List[CurrentHolding]:
        """
        Get current portfolio holdings.
        
        Args:
            wallet_address: Wallet to analyze
        
        Returns:
            List of current holdings
        """
        from wallet.wallet_integration import WalletManager
        
        wallet = WalletManager(default_network=self.network)
        wallet_address = Web3.to_checksum_address(wallet_address)
        
        holdings = []
        total_value = Decimal("0")
        
        # Get native balance
        native_balance = wallet.get_native_balance(wallet_address)
        # In production, get price from oracle
        native_price = Decimal("2000")  # Placeholder ETH price
        native_value = native_balance * native_price
        total_value += native_value
        
        holdings.append(CurrentHolding(
            token_address=self.NATIVE_TOKEN,
            symbol="ETH",
            balance=native_balance,
            value_usd=native_value,
            current_percent=Decimal("0")  # Calculate after total
        ))
        
        # Get token balances for each target
        for target in self._targets:
            if target.token_address == self.NATIVE_TOKEN:
                continue
            
            try:
                token_info = wallet.get_token_balance(
                    wallet_address, target.token_address
                )
                
                # Get price (placeholder)
                token_price = Decimal("1")  # Would use price oracle
                token_value = token_info.balance * token_price
                total_value += token_value
                
                holdings.append(CurrentHolding(
                    token_address=target.token_address,
                    symbol=target.symbol,
                    balance=token_info.balance,
                    value_usd=token_value,
                    current_percent=Decimal("0")
                ))
            except Exception as e:
                logger.warning(f"Error getting balance for {target.symbol}: {e}")
        
        # Calculate percentages
        if total_value > 0:
            for holding in holdings:
                holding.current_percent = (holding.value_usd / total_value) * 100
        
        return holdings
    
    def calculate_rebalance_trades(
        self,
        wallet_address: str,
        force: bool = False
    ) -> RebalancePlan:
        """
        Calculate trades needed to rebalance portfolio.
        
        Args:
            wallet_address: Wallet to rebalance
            force: Force calculation even if within thresholds
        
        Returns:
            Rebalance plan with required trades
        """
        if not self._targets:
            return RebalancePlan(
                trades=[],
                total_portfolio_value=Decimal("0"),
                estimated_gas_cost=Decimal("0"),
                estimated_slippage=Decimal("0"),
                needs_rebalance=False
            )
        
        holdings = self.get_current_holdings(wallet_address)
        total_value = sum(h.value_usd for h in holdings)
        
        if total_value == 0:
            return RebalancePlan(
                trades=[],
                total_portfolio_value=Decimal("0"),
                estimated_gas_cost=Decimal("0"),
                estimated_slippage=Decimal("0"),
                needs_rebalance=False
            )
        
        # Build lookup maps
        holdings_map = {h.token_address: h for h in holdings}
        targets_map = {t.token_address: t for t in self._targets}
        
        trades = []
        needs_rebalance = False
        
        for target in self._targets:
            holding = holdings_map.get(target.token_address)
            current_percent = holding.current_percent if holding else Decimal("0")
            current_value = holding.value_usd if holding else Decimal("0")
            
            diff_percent = current_percent - target.target_percent
            
            # Check if outside thresholds
            outside_threshold = (
                current_percent < target.min_percent or
                current_percent > target.max_percent
            )
            
            if outside_threshold or force:
                needs_rebalance = True
                
                # Calculate trade
                target_value = total_value * (target.target_percent / 100)
                trade_value = abs(target_value - current_value)
                
                if trade_value >= self.min_trade_value_usd:
                    direction = TradeDirection.BUY if diff_percent < 0 else TradeDirection.SELL
                    
                    # Calculate amount based on price (placeholder)
                    token_price = Decimal("1")  # Would use oracle
                    amount = trade_value / token_price
                    
                    trades.append(RebalanceTrade(
                        token_address=target.token_address,
                        symbol=target.symbol,
                        direction=direction,
                        amount=amount,
                        value_usd=trade_value,
                        from_percent=current_percent,
                        to_percent=target.target_percent
                    ))
        
        # Estimate costs
        estimated_gas = Decimal("0.01") * len(trades)  # ~$20 per swap
        estimated_slippage = sum(t.value_usd for t in trades) * (self.slippage_tolerance / 100)
        
        return RebalancePlan(
            trades=trades,
            total_portfolio_value=total_value,
            estimated_gas_cost=estimated_gas,
            estimated_slippage=estimated_slippage,
            needs_rebalance=needs_rebalance
        )
    
    def execute_rebalance(
        self,
        plan: RebalancePlan,
        private_key: str,
        dry_run: bool = False
    ) -> RebalanceResult:
        """
        Execute a rebalance plan.
        
        Args:
            plan: Rebalance plan to execute
            private_key: Wallet private key
            dry_run: If True, simulate without executing
        
        Returns:
            Execution result
        """
        if not plan.needs_rebalance or not plan.trades:
            return RebalanceResult(
                success=True,
                executed_trades=[],
                failed_trades=[],
                total_gas_used=0,
                total_value_traded=Decimal("0")
            )
        
        if dry_run:
            logger.info("DRY RUN - Simulating rebalance")
            return RebalanceResult(
                success=True,
                executed_trades=[
                    {
                        "symbol": t.symbol,
                        "direction": t.direction.value,
                        "amount": str(t.amount),
                        "value_usd": str(t.value_usd),
                        "simulated": True
                    }
                    for t in plan.trades
                ],
                failed_trades=[],
                total_gas_used=0,
                total_value_traded=plan.total_trade_value
            )
        
        # In production, execute swaps via DEX router
        executed = []
        failed = []
        total_gas = 0
        
        # Sort: sells first, then buys
        sorted_trades = sorted(
            plan.trades,
            key=lambda t: 0 if t.direction == TradeDirection.SELL else 1
        )
        
        for trade in sorted_trades:
            try:
                logger.info(
                    f"Executing {trade.direction.value} {trade.amount} {trade.symbol}"
                )
                
                # Placeholder - would call DEX router
                result = self._execute_swap(trade, private_key)
                
                if result["success"]:
                    executed.append({
                        "symbol": trade.symbol,
                        "direction": trade.direction.value,
                        "amount": str(trade.amount),
                        "tx_hash": result.get("tx_hash"),
                        "gas_used": result.get("gas_used", 0)
                    })
                    total_gas += result.get("gas_used", 0)
                else:
                    failed.append({
                        "symbol": trade.symbol,
                        "direction": trade.direction.value,
                        "amount": str(trade.amount),
                        "error": result.get("error")
                    })
                    
            except Exception as e:
                logger.error(f"Trade failed for {trade.symbol}: {e}")
                failed.append({
                    "symbol": trade.symbol,
                    "direction": trade.direction.value,
                    "amount": str(trade.amount),
                    "error": str(e)
                })
        
        success = len(failed) == 0
        
        return RebalanceResult(
            success=success,
            executed_trades=executed,
            failed_trades=failed,
            total_gas_used=total_gas,
            total_value_traded=sum(
                Decimal(t["amount"]) for t in executed
            ) if executed else Decimal("0"),
            error=f"{len(failed)} trades failed" if failed else None
        )
    
    def _execute_swap(
        self,
        trade: RebalanceTrade,
        private_key: str
    ) -> Dict[str, Any]:
        """
        Execute a single swap.
        
        In production, this would integrate with:
        - Uniswap
        - 1inch
        - Paraswap
        - 0x
        """
        # Placeholder implementation
        logger.info(f"Would swap {trade.amount} {trade.symbol}")
        
        return {
            "success": True,
            "tx_hash": "0x" + "0" * 64,
            "gas_used": 150000
        }
    
    def check_needs_rebalance(self, wallet_address: str) -> bool:
        """Quick check if rebalance is needed."""
        plan = self.calculate_rebalance_trades(wallet_address)
        return plan.needs_rebalance
    
    def get_allocation_drift(
        self,
        wallet_address: str
    ) -> Dict[str, Decimal]:
        """
        Get current drift from target allocations.
        
        Returns:
            Dictionary of symbol -> drift percentage
        """
        holdings = self.get_current_holdings(wallet_address)
        holdings_map = {h.token_address: h for h in holdings}
        
        drift = {}
        for target in self._targets:
            holding = holdings_map.get(target.token_address)
            current = holding.current_percent if holding else Decimal("0")
            drift[target.symbol] = current - target.target_percent
        
        return drift
