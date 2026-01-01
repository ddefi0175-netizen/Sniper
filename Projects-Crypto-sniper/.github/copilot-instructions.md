# Crypto Sniper - AI Coding Instructions

## Project Overview
Crypto Sniper is a multi-chain DeFi automation platform for trading, staking, yield farming, NFT management, and portfolio analytics. Built with Python (FastAPI backend) and Web3.py for blockchain interactions across 10+ EVM chains.

## Architecture

### Core Components
- **`config/`** - Settings and multi-chain network configs (`networks.py`)
- **`auth/`** - Web3 wallet authentication with JWT tokens (`wallet_auth.py`)
- **`contracts/`** - Smart contract interaction manager (`SmartContractManager`)
- **`wallet/`** - Multi-chain wallet operations with ERC20 support (`WalletManager`)
- **`realtime/`** - WebSocket handlers for live price/transaction feeds
- **`backend/staking/`** - Staking and yield farming management
- **`backend/ai_predict.py`** - FastAPI endpoint for market prediction

### New Modules (v1.1)
- **`middleware/rate_limiter.py`** - API rate limiting with token bucket algorithm
- **`multisig/multisig_manager.py`** - Multi-signature wallet management
- **`nft/nft_manager.py`** - ERC721/ERC1155 NFT operations
- **`rebalance/rebalance_manager.py`** - Portfolio auto-rebalancing

### Data Flow Pattern
1. User authenticates via wallet signature → `WalletAuthenticator.verify_signature()`
2. Rate limiter validates request → `RateLimiter.check_rate_limit()`
3. Operations use `SmartContractManager` for blockchain reads/writes
4. Multi-chain support via `get_network_config(network)` from `config.networks`

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

### Rate Limiting
```python
from middleware.rate_limiter import RateLimiter, RateLimitConfig

config = RateLimitConfig(requests_per_minute=60)
limiter = RateLimiter(config)

# Check rate limit
result = limiter.check_rate_limit(client_id="user_123")
if not result.allowed:
    return {"error": "Rate limit exceeded", "retry_after": result.retry_after}
```

### Multi-Sig Transactions
```python
from multisig.multisig_manager import MultiSigManager

multisig = MultiSigManager(network="ethereum")
wallet = multisig.create_wallet(
    owners=["0x...", "0x...", "0x..."],
    threshold=2
)
proposal = multisig.create_proposal(wallet.address, to="0x...", value=1e18)
```

### NFT Operations
```python
from nft.nft_manager import NFTManager

nft_mgr = NFTManager(network="ethereum")
nfts = nft_mgr.get_nfts(wallet_address)
result = nft_mgr.transfer_nft(contract, token_id, to_address, private_key)
```

### Portfolio Rebalancing
```python
from rebalance.rebalance_manager import RebalanceManager, AllocationTarget

rebalancer = RebalanceManager(network="ethereum")
rebalancer.set_target_allocation([
    AllocationTarget("0xEee...", "ETH", Decimal("50")),
    AllocationTarget("0x...", "USDC", Decimal("30")),
    AllocationTarget("0x...", "WBTC", Decimal("20")),
])
plan = rebalancer.calculate_rebalance_trades(wallet_address)
if plan.needs_rebalance:
    result = rebalancer.execute_rebalance(plan, private_key)
```

### Type Hints & Dataclasses
All public interfaces use dataclasses for structured returns:
- `AuthResult`, `ContractCall`, `WalletInfo`, `TokenInfo`
- `PoolInfo`, `StakePosition`, `RateLimitResult`
- `NFTInfo`, `NFTCollection`, `NFTTransferResult`
- `MultiSigWallet`, `MultiSigProposal`, `AllocationTarget`, `RebalancePlan`

## Development Workflow

### Setup
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements-dev.txt
cp .env.example .env  # Configure environment
```

### Run Services
```bash
# Development server
python scripts/run_dev.py

# Or directly with uvicorn
uvicorn backend.ai_predict:app --reload --port 8000

# Run tests
pytest
pytest --cov=. --cov-report=html

# Health check
python scripts/health_check.py
```

### Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### CI Pipeline
Uses GitHub Actions via `.github/workflows/python-package-conda.yml`:
- Python 3.10, flake8 linting, pytest
- CodeQL security scanning (monthly)

## Supported Networks
Defined in `config/networks.py`:

**Mainnets**: `ethereum`, `bsc`, `polygon`, `arbitrum`, `optimism`, `avalanche`, `fantom`, `base`

**Testnets**: `goerli`, `sepolia`, `mumbai`, `bsc_testnet`

## Key Conventions
- **Formatting**: Black, isort (run pre-commit hooks)
- **Async I/O**: Use `asyncio` for WebSocket/blockchain polling operations
- **Decimal precision**: Always use `Decimal` for token amounts, never `float`
- **Address handling**: Always convert to checksum via `Web3.to_checksum_address()`
- **Logging**: Use module-level `logger = logging.getLogger(__name__)`
- **Error handling**: Return result dataclasses with `success: bool` and `error: Optional[str]`

## File Structure
```
crypto-sniper/
├── .github/
│   └── workflows/          # CI/CD pipelines
├── config/                 # Settings and network configs
├── auth/                   # Wallet authentication
├── contracts/              # Smart contract manager
├── wallet/                 # Wallet operations
├── realtime/               # WebSocket handlers
├── middleware/             # Rate limiting, auth middleware
├── multisig/               # Multi-sig wallet management
├── nft/                    # NFT operations
├── rebalance/              # Portfolio rebalancing
├── backend/                # FastAPI application
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── Dockerfile              # Container build
├── docker-compose.yml      # Service orchestration
└── requirements.txt        # Dependencies
```
