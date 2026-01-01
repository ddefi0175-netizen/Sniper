# Crypto Sniper - AI Coding Instructions

## Project Overview
Crypto Sniper is a multi-chain DeFi automation platform for trading, staking, yield farming, and portfolio analytics. Built with Python (FastAPI backend) and Web3.py for blockchain interactions across 8+ EVM chains.

## Architecture

### Core Components
- **`backend_config/`** - Settings (`settings_.txt`) and multi-chain network configs (`networks.py`)
- **`backend_auth/`** - Web3 wallet authentication with JWT tokens and signature verification
- **`backend_contracts/`** - Smart contract interaction manager (`SmartContractManager`)
- **`backend_wallet/`** - Multi-chain wallet operations with ERC20 support (`WalletManager`)
- **`backend_realtime/`** - WebSocket handlers for live price/transaction feeds
- **`backend/staking/`** - Staking and yield farming management
- **`backend/ai_predict.py`** - FastAPI endpoint for market prediction

### Data Flow Pattern
1. User authenticates via wallet signature → `WalletAuthenticator.verify_signature()`
2. Operations use `SmartContractManager` for blockchain reads/writes
3. Multi-chain support via `get_network_config(network)` from `config.networks`

## Critical Security Rules

**NEVER commit secrets** - Use environment variables:
```python
# ✓ Correct
os.getenv("INFURA_API_KEY")
os.getenv("JWT_SECRET_KEY")

# ✗ Never hardcode
private_key = "0x..."
```

**Required env vars**: `INFURA_API_KEY`, `ALCHEMY_API_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`

**Testnet-first development**: Always use `is_testnet=True` networks (sepolia, goerli) before mainnet.

## Code Patterns

### Multi-chain Contract Calls
```python
from config.networks import get_network_config
from contracts.smart_contract import SmartContractManager

manager = SmartContractManager(network="polygon", private_key=None)  # read-only
contract = manager.load_contract(address, abi)
result = manager.read_contract(contract, "balanceOf", wallet_address)
```

### Wallet Operations
```python
from wallet.wallet_integration import WalletManager

wallet_mgr = WalletManager(default_network="ethereum")
info = wallet_mgr.get_wallet_info(address)  # Returns WalletInfo dataclass
```

### Type Hints & Dataclasses
All public interfaces use dataclasses for structured returns:
- `AuthResult`, `ContractCall`, `WalletInfo`, `TokenInfo`, `PoolInfo`, `StakePosition`

## Development Workflow

### Setup
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements-dev.txt
```

### Run Services
```bash
# AI prediction API
uvicorn backend.ai_predict:app --reload --port 8000

# Tests
pytest
```

### CI Pipeline
Uses Conda environment via `.github/workflows/python-package-conda.yml`:
- Python 3.10, flake8 linting, pytest

## Supported Networks
Defined in `backend_config_networks.py`: `ethereum`, `bsc`, `polygon`, `arbitrum`, `optimism`, `avalanche`, `fantom`, `base` (+ testnets: `goerli`, `sepolia`)

## Key Conventions
- **Formatting**: Black, isort (run pre-commit hooks)
- **Async I/O**: Use `asyncio` for WebSocket/blockchain polling operations
- **Decimal precision**: Always use `Decimal` for token amounts, never `float`
- **Address handling**: Always convert to checksum via `Web3.to_checksum_address()`
- **Logging**: Use module-level `logger = logging.getLogger(__name__)`
