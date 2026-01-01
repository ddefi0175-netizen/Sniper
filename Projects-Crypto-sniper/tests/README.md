# Crypto Sniper Test Suite

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_wallet.py

# Run specific test
pytest tests/test_wallet.py::TestWalletManager::test_get_native_balance

# Run with markers
pytest -m "not slow"          # Skip slow tests
pytest -m "integration"        # Only integration tests

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

## Test Structure

```text
tests/
├── conftest.py          # Shared fixtures
├── test_auth.py         # Authentication tests
├── test_wallet.py       # Wallet operations
├── test_staking.py      # Staking/farming
├── test_rate_limiter.py # Rate limiting
├── test_nft.py          # NFT manager
├── test_rebalance.py    # Portfolio rebalance
└── test_contracts.py    # Smart contracts (TODO)
```

## Writing Tests

```python
import pytest
from decimal import Decimal

class TestMyFeature:
    """Tests for MyFeature."""
    
    def test_basic_functionality(self, mock_web3):
        """Test basic case."""
        result = my_function()
        assert result is not None
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """Test that takes a long time."""
        pass
    
    @pytest.mark.integration
    def test_external_service(self):
        """Test requiring external service."""
        pass
    
    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_with_parameters(self, input, expected):
        """Test with multiple inputs."""
        assert input * 2 == expected
```

## Available Fixtures

From `conftest.py`:

- `mock_web3` - Mocked Web3 instance
- `mock_network_config` - Mocked network configuration
- `test_wallet_address` - Test wallet address
- `test_contract_address` - Test contract address
- `test_private_key` - Test private key
- `sample_token_info` - Sample token data
- `sample_wallet_info` - Sample wallet data
- `sample_stake_position` - Sample staking position
- `mock_contract` - Factory for mock contracts

## Coverage Requirements

- Minimum coverage: 80%
- Critical paths: 100%
- All public functions must have tests
