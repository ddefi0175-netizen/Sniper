# 🎯 Crypto Sniper

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A multi-chain DeFi automation platform** for trading, staking, yield farming, governance, and portfolio analytics across 10+ EVM-compatible blockchains.

---

## 🌟 Features

| Module | Description |
|--------|-------------|
| 🔐 **Wallet Authentication** | Web3 signature-based auth with JWT tokens |
| 📜 **Smart Contracts** | Read/write contract interactions with event subscriptions |
| 💰 **Multi-Chain Wallet** | Balance tracking, ENS support, ERC20 operations |
| 📡 **Real-Time Data** | WebSocket feeds for prices, transactions, blocks |
| 🥩 **Staking & Farming** | Stake tokens, claim rewards, manage LP positions |
| 🗳️ **DAO Governance** | Create proposals, vote, delegate voting power |
| 📊 **Analytics Dashboard** | Portfolio metrics, P&L tracking, allocation analysis |
| 🤖 **AI Predictions** | Market analysis API endpoint |

---

## 🔗 Supported Networks

| Network | Chain ID | Type |
|---------|----------|------|
| Ethereum | 1 | Mainnet |
| BNB Smart Chain | 56 | Mainnet |
| Polygon | 137 | Mainnet |
| Arbitrum One | 42161 | L2 |
| Optimism | 10 | L2 |
| Avalanche C-Chain | 43114 | Mainnet |
| Fantom Opera | 250 | Mainnet |
| Base | 8453 | L2 |
| Goerli | 5 | Testnet |
| Sepolia | 11155111 | Testnet |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip or conda

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-sniper.git
cd crypto-sniper

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values (NEVER commit .env!)
```

**Required Environment Variables:**

```env
JWT_SECRET_KEY=your-secure-random-string
INFURA_API_KEY=your-infura-key
ALCHEMY_API_KEY=your-alchemy-key
DATABASE_URL=sqlite:///./web3_app.db
REDIS_URL=redis://localhost:6379
```

### Run the API Server

```bash
uvicorn backend.ai_predict:app --reload --port 8000
```

---

## 📚 API Reference

### 🔐 Authentication Module

#### `WalletAuthenticator`

Web3 wallet-based authentication using signature verification.

```python
from auth.wallet_auth import WalletAuthenticator

auth = WalletAuthenticator()

# Step 1: Generate nonce for user
nonce = auth.generate_nonce("0x742d35Cc6634C0532925a3b844Bc9e7595f...")

# Step 2: User signs message in their wallet
message = auth.get_sign_message(address, nonce)

# Step 3: Verify signature and get JWT token
result = auth.verify_signature(address, signature)
if result.success:
    print(f"Token: {result.token}")
    print(f"Expires: {result.expires_at}")
```

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `generate_nonce(address)` | Create unique nonce for signing | `str` |
| `get_sign_message(address, nonce)` | Get message to be signed | `str` |
| `verify_signature(address, signature)` | Verify and authenticate | `AuthResult` |
| `verify_token(token)` | Validate JWT token | `AuthResult` |
| `refresh_token(token)` | Refresh existing token | `AuthResult` |
| `revoke_token(token)` | Logout/invalidate token | `bool` |

---

### 📜 Smart Contract Module

#### `SmartContractManager`

Interact with any smart contract on supported networks.

```python
from contracts.smart_contract import SmartContractManager

# Read-only mode (no private key)
manager = SmartContractManager(network="polygon")

# With signing capability
manager = SmartContractManager(
    network="polygon",
    private_key=os.getenv("PRIVATE_KEY")
)

# Load contract
contract = manager.load_contract(address, abi)

# Read data (view functions)
result = manager.read_contract(contract, "balanceOf", wallet_address)
print(f"Balance: {result.data}")

# Write data (state-changing)
result = manager.write_contract(
    contract, 
    "transfer",
    recipient_address,
    amount,
    gas_limit=100000
)
print(f"TX Hash: {result.tx_hash}")
```

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `load_contract(address, abi)` | Load contract instance | `Contract` |
| `read_contract(contract, func, *args)` | Call view function | `ContractCall` |
| `write_contract(contract, func, *args)` | Execute transaction | `ContractCall` |
| `estimate_gas(contract, func, *args)` | Estimate gas cost | `int` |
| `get_events(contract, event, from_block)` | Query past events | `List[Dict]` |
| `subscribe_to_events(contract, event, callback)` | Live event stream | `str` |

---

### 💰 Wallet Module

#### `WalletManager`

Multi-chain wallet operations with ERC20 and ENS support.

```python
from wallet.wallet_integration import WalletManager

wallet = WalletManager(default_network="ethereum")

# Get comprehensive wallet info
info = wallet.get_wallet_info("0x742d35Cc...")
print(f"Balance: {info.native_balance} ETH")
print(f"ENS: {info.ens_name}")

# Get ERC20 token balance
balance = wallet.get_token_balance(
    wallet_address="0x742d35Cc...",
    token_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
    network="ethereum"
)

# Resolve ENS name
address = wallet.resolve_ens("vitalik.eth")

# Get gas prices
gas = wallet.get_gas_price("ethereum")
print(f"Gas: {gas['gas_price_gwei']} Gwei")
```

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `get_wallet_info(address)` | Full wallet details | `WalletInfo` |
| `get_native_balance(address)` | Native token balance | `Decimal` |
| `get_token_balance(wallet, token)` | ERC20 balance | `Decimal` |
| `get_token_info(token_address)` | Token metadata | `TokenInfo` |
| `resolve_ens(name)` | ENS to address | `str` |
| `reverse_ens(address)` | Address to ENS | `str` |
| `get_gas_price(network)` | Current gas prices | `Dict` |
| `get_supported_networks()` | List all networks | `List[Dict]` |

---

### 📡 Real-Time Module

#### `WebSocketManager`

Manage real-time data subscriptions.

```python
from realtime.websocket_handler import WebSocketManager, PriceFeed

ws = WebSocketManager()

# Subscribe to price updates
sub_id = await ws.subscribe(
    client_id="user123",
    subscription_type="price",
    params={"token": "ETH"},
    callback=handle_price_update
)

# Broadcast to subscribers
await ws.broadcast("price", {"token": "ETH", "price": "2500.00"})

# Unsubscribe
await ws.unsubscribe(sub_id)
```

#### `PriceFeed`

```python
price_feed = PriceFeed(ws_manager)
price_feed.add_token("ETH", initial_price=Decimal("2500"))

# Start real-time feed
await price_feed.start()

# Get cached price
price = price_feed.get_price("ETH")
```

#### `TransactionMonitor`

```python
from realtime.websocket_handler import TransactionMonitor

monitor = TransactionMonitor(ws_manager, network="ethereum")

# Monitor specific transaction
monitor.monitor_transaction("0xabc123...")

# Monitor all txs for an address
monitor.monitor_address("0x742d35Cc...")

await monitor.start()
```

---

### 🥩 Staking Module

#### `StakingManager`

Manage staking pools and yield farming.

```python
from staking.staking_manager import StakingManager

staking = StakingManager(network="ethereum", private_key=key)

# Register a staking pool
pool = staking.register_pool(
    pool_id="eth-staking-v1",
    contract_address="0x...",
    name="ETH Staking Pool",
    staking_token="0x...",
    reward_token="0x...",
    lock_period=86400 * 7,  # 7 days
    min_stake=Decimal("0.1")
)
print(f"APY: {pool.apy}%")

# Stake tokens
result = staking.stake(
    pool_id="eth-staking-v1",
    contract_address="0x...",
    amount=Decimal("1.5")
)

# Check pending rewards
rewards = staking.get_pending_rewards(
    user_address="0x...",
    pool_id="eth-staking-v1",
    contract_address="0x..."
)

# Claim rewards
staking.claim_rewards(pool_id, contract_address)

# Unstake
staking.unstake(pool_id, contract_address, amount)

# Exit pool (unstake all + claim)
staking.exit_pool(pool_id, contract_address)
```

**Methods:**

| Method | Description | Returns |
|--------|-------------|---------|
| `register_pool(...)` | Add staking pool | `PoolInfo` |
| `stake(pool_id, address, amount)` | Stake tokens | `Dict` |
| `unstake(pool_id, address, amount)` | Withdraw stake | `Dict` |
| `claim_rewards(pool_id, address)` | Claim pending rewards | `Dict` |
| `exit_pool(pool_id, address)` | Full exit | `Dict` |
| `get_staked_balance(user, pool)` | User's stake | `Decimal` |
| `get_pending_rewards(user, pool)` | Unclaimed rewards | `Decimal` |
| `get_pool_statistics(pool_id)` | Pool metrics | `Dict` |

---

### 🗳️ Governance Module

#### `DAOManager`

Interact with DAO governance contracts.

```python
from governance.dao_manager import DAOManager

dao = DAOManager(
    governor_address="0x...",
    network="ethereum",
    private_key=key
)

# Create proposal
result = dao.create_proposal(
    title="Increase Staking Rewards",
    description="Proposal to increase APY by 2%",
    targets=["0x..."],  # Contract addresses
    values=[0],          # ETH values
    calldatas=[encoded_call]
)

# Vote on proposal
dao.cast_vote(
    proposal_id=1,
    support=1,  # 0=against, 1=for, 2=abstain
    reason="Great improvement for the protocol"
)

# Check proposal status
state = dao.get_proposal_state(proposal_id=1)
votes = dao.get_proposal_votes(proposal_id=1)
print(f"For: {votes['for']}, Against: {votes['against']}")

# Execute passed proposal
dao.execute_proposal(targets, values, calldatas, description_hash)
```

#### `VotingManager`

```python
from governance.voting import VotingManager

voting = VotingManager(token_address="0x...", network="ethereum")

# Get voting power
power = voting.get_voting_power("0x742d35Cc...")
print(f"Votes: {power.total_power}")

# Delegate votes
voting.delegate(delegatee="0x...")

# Self-delegate to activate voting
voting.self_delegate()
```

---

### 📊 Analytics Module

#### Data Classes

```python
from analytics.dashboard import TokenHolding, PortfolioMetrics

# TokenHolding - Individual asset
holding = TokenHolding(
    token_address="0x...",
    symbol="ETH",
    name="Ethereum",
    balance=Decimal("5.5"),
    price_usd=Decimal("2500"),
    value_usd=Decimal("13750"),
    change_24h=Decimal("2.5"),
    allocation_percent=Decimal("45.2")
)

# PortfolioMetrics - Full portfolio
portfolio = PortfolioMetrics(
    total_value_usd=Decimal("30000"),
    total_change_24h=Decimal("750"),
    total_change_percent_24h=Decimal("2.5"),
    holdings=[holding],
    native_balance=Decimal("5.5"),
    native_value_usd=Decimal("13750"),
    defi_positions_value=Decimal("10000"),
    nft_value=Decimal("5000")
)
```

---

### 🤖 AI Prediction API

```python
# FastAPI endpoint at /predict
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"symbol": "ETH"}
)
result = response.json()
# {
#     "symbol": "ETH",
#     "suggest_buy": true,
#     "confidence": 0.6,
#     "analysis_text": "Market analysis for ETH..."
# }
```

---

## 🔒 Security Best Practices

### ⚠️ Critical Rules

1. **NEVER commit secrets** to the repository

   ```python
   # ✅ Correct
   private_key = os.getenv("PRIVATE_KEY")
   
   # ❌ NEVER do this
   private_key = "0xabc123..."
   ```

2. **Use testnets first** - Always test on Goerli/Sepolia before mainnet

3. **Validate all addresses** using checksums

   ```python
   address = Web3.to_checksum_address(user_input)
   ```

4. **Use Decimal for token amounts** - Never `float`

   ```python
   from decimal import Decimal
   amount = Decimal("1.5")  # ✅
   amount = 1.5  # ❌
   ```

---

## 📁 Project Structure

```
crypto-sniper/
├── config/
│   ├── __init__.py
│   ├── networks.py      # Chain configurations
│   └── settings.py      # App settings
├── auth/
│   ├── __init__.py
│   ├── wallet_auth.py   # JWT + Web3 auth
│   └── permissions.py   # RBAC system
├── contracts/
│   ├── __init__.py
│   └── smart_contract.py
├── wallet/
│   ├── __init__.py
│   └── wallet_integration.py
├── realtime/
│   ├── __init__.py
│   └── websocket_handler.py
├── staking/
│   ├── __init__.py
│   └── staking_manager.py
├── governance/
│   ├── __init__.py
│   ├── dao_manager.py
│   └── voting.py
├── analytics/
│   ├── __init__.py
│   └── dashboard.py
├── backend/
│   └── ai_predict.py    # FastAPI app
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific module tests
pytest tests/test_wallet.py -v
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feat/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Adding tests

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

This software is for educational purposes. Cryptocurrency trading involves substantial risk of loss. Always:

- Use testnet for development
- Start with small amounts
- Never invest more than you can afford to lose
- DYOR (Do Your Own Research)

---

## 📞 Support

- 📧 Email: <support@example.com>
- 💬 Discord: [Join Server](#)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/crypto-sniper/issues)
