"""
Pytest configuration and fixtures for Crypto Sniper tests.
"""

import pytest
from decimal import Decimal
from typing import Generator
from unittest.mock import Mock, patch


# Test addresses
TEST_WALLET = "0x742d35Cc6634C0532925a3b844Bc9e7595f5bAb2"
TEST_CONTRACT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC
TEST_PRIVATE_KEY = "0x" + "1" * 64  # Fake key for testing


@pytest.fixture
def mock_web3():
    """Mock Web3 instance."""
    with patch("web3.Web3") as mock:
        instance = Mock()
        instance.eth.chain_id = 1
        instance.eth.gas_price = 20000000000  # 20 gwei
        instance.eth.get_transaction_count.return_value = 0
        instance.is_connected.return_value = True
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_network_config():
    """Mock network configuration."""
    with patch("config.networks.get_network_config") as mock:
        mock.return_value = Mock(
            rpc_url="http://localhost:8545",
            chain_id=1,
            native_symbol="ETH",
            explorer_url="https://etherscan.io",
            is_testnet=True
        )
        yield mock


@pytest.fixture
def test_wallet_address() -> str:
    """Return test wallet address."""
    return TEST_WALLET


@pytest.fixture
def test_contract_address() -> str:
    """Return test contract address."""
    return TEST_CONTRACT


@pytest.fixture
def test_private_key() -> str:
    """Return test private key."""
    return TEST_PRIVATE_KEY


@pytest.fixture
def sample_token_info() -> dict:
    """Sample token information."""
    return {
        "address": TEST_CONTRACT,
        "symbol": "USDC",
        "name": "USD Coin",
        "decimals": 6,
        "balance": Decimal("1000.00"),
        "balance_raw": 1000000000
    }


@pytest.fixture
def sample_wallet_info() -> dict:
    """Sample wallet information."""
    return {
        "address": TEST_WALLET,
        "native_balance": Decimal("1.5"),
        "native_balance_raw": 1500000000000000000,
        "native_symbol": "ETH"
    }


@pytest.fixture
def sample_stake_position() -> dict:
    """Sample staking position."""
    return {
        "protocol": "test_protocol",
        "pool_id": "1",
        "staked_amount": Decimal("100.0"),
        "rewards_pending": Decimal("5.5"),
        "apy": Decimal("12.5"),
        "lock_end": None
    }


@pytest.fixture
def sample_allocation_targets() -> list:
    """Sample portfolio allocation targets."""
    return [
        {"token_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "symbol": "ETH", "target_percent": Decimal("50")},
        {"token_address": TEST_CONTRACT, "symbol": "USDC", "target_percent": Decimal("30")},
        {"token_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "symbol": "WBTC", "target_percent": Decimal("20")},
    ]


class MockContractFunction:
    """Mock contract function for testing."""
    
    def __init__(self, return_value):
        self._return_value = return_value
    
    def call(self):
        return self._return_value
    
    def build_transaction(self, tx_params):
        return {
            "to": "0x" + "0" * 40,
            "data": "0x",
            "gas": 100000,
            "gasPrice": 20000000000,
            "nonce": 0,
            **tx_params
        }
    
    def estimate_gas(self, params=None):
        return 100000


class MockContract:
    """Mock contract for testing."""
    
    def __init__(self, functions_map: dict = None):
        self._functions_map = functions_map or {}
    
    @property
    def functions(self):
        return self
    
    def __getattr__(self, name):
        def method(*args, **kwargs):
            if name in self._functions_map:
                return MockContractFunction(self._functions_map[name])
            return MockContractFunction(None)
        return method


@pytest.fixture
def mock_contract():
    """Create a mock contract factory."""
    def _create_mock(functions_map: dict = None):
        return MockContract(functions_map)
    return _create_mock


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("INFURA_API_KEY", "test_infura_key")
    monkeypatch.setenv("ALCHEMY_API_KEY", "test_alchemy_key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_jwt_secret_key_for_testing")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")


# Markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "mainnet: marks tests that require mainnet connection"
    )
