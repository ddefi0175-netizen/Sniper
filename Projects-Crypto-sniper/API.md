# API Reference

Complete API documentation for Crypto Sniper modules.

---

## Table of Contents

- [Authentication](#authentication)
- [Smart Contracts](#smart-contracts)
- [Wallet Operations](#wallet-operations)
- [Real-Time Services](#real-time-services)
- [Staking & Yield](#staking--yield)
- [Governance](#governance)
- [Analytics](#analytics)
- [AI Predictions](#ai-predictions)

---

## Authentication

### WalletAuthenticator

Web3 wallet authentication with JWT tokens.

```python
from auth.wallet_auth import WalletAuthenticator

auth = WalletAuthenticator()
```

#### Methods

##### `generate_nonce()`

Generate a random nonce for signature challenges.

```python
nonce = auth.generate_nonce()
# Returns: "0x7f2a3b9c4d5e6f..."
```

**Returns:** `str` - 32-byte hex string

---

##### `verify_signature(address, message, signature)`

Verify a wallet signature.

```python
is_valid = auth.verify_signature(
    address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    message="Sign this message: abc123",
    signature="0x..."
)
```

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| address | str | Wallet address that signed |
| message | str | Original message |
| signature | str | Signature hex string |

**Returns:** `bool` - True if signature is valid

---

##### `create_token(wallet_address)`

Create a JWT token for authenticated session.

```python
token = auth.create_token("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
# Returns: "eyJhbGciOiJIUzI1NiIs..."
```

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| wallet_address | str | Authenticated wallet address |

**Returns:** `str` - JWT token string

---

##### `verify_token(token)`

Verify and decode a JWT token.

```python
result = auth.verify_token("eyJhbGciOiJIUzI1NiIs...")
if result.authenticated:
    print(f"Wallet: {result.wallet_address}")
```

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| token | str | JWT token to verify |

**Returns:** `AuthResult` dataclass with:

- `authenticated: bool`
- `wallet_address: str`
- `token: str`
- `expires_at: str`
- `error: str | None`

---

## Smart Contracts

### SmartContractManager

Interact with smart contracts on any supported network.

```python
from contracts.smart_contract import SmartContractManager

# Read-only (no private key)
manager = SmartContractManager(network="ethereum")

# With write capability
manager = SmartContractManager(
    network="polygon",
    private_key="0x..."
)
```

#### Constructor Parameters

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| network | str | "ethereum" | Network name |
| private_key | str | None | For signing transactions |

---

#### SmartContractManager Methods

##### `load_contract(address, abi)`

Load a contract instance.

```python
contract = manager.load_contract(
    address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    abi=USDC_ABI
)
```

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| address | str | Contract address |
| abi | list | Contract ABI |

**Returns:** `Contract` - Web3 contract instance

---

##### `read_contract(contract, function_name, *args)`

Call a read-only contract function.

```python
balance = manager.read_contract(
    contract,
    "balanceOf",
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
)
decimals = manager.read_contract(contract, "decimals")
```

**Parameters:**

| Name | Type | Description |
| --- | --- | --- |
| contract | Contract | Contract instance |
| function_name | str | Function to call |
| *args | Any | Function arguments |

**Returns:** `Any` - Function return value

---

##### `write_contract(contract, function_name, *args, value=0, gas_limit=None)`

Execute a state-changing transaction.

```python
result = manager.write_contract(
    contract,
    "transfer",
    "0xRecipient...",
    1000000,  # amount
    gas_limit=100000
)

if result.success:
    print(f"TX: {result.tx_hash}")
```

**Parameters:**

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| contract | Contract | - | Contract instance |
| function_name | str | - | Function to call |
| *args | Any | - | Function arguments |
| value | int | 0 | ETH to send (wei) |
| gas_limit | int | None | Gas limit |

**Returns:** `ContractCall` dataclass with:

- `success: bool`
- `tx_hash: str`
- `gas_used: int`
- `block_number: int`
- `error: str | None`

---

##### `estimate_gas(contract, function_name, *args)`

Estimate gas for a transaction.

```python
gas = manager.estimate_gas(
    contract,
    "transfer",
    "0xRecipient...",
    1000000
)
print(f"Estimated gas: {gas}")
```

**Returns:** `int` - Estimated gas units

---

##### `subscribe_events(contract, event_name, callback, from_block="latest")`

Subscribe to contract events.

```python
def handle_transfer(event):
    print(f"Transfer: {event['args']['from']} -> {event['args']['to']}")

manager.subscribe_events(
    contract,
    "Transfer",
    handle_transfer
)
```

---

## Wallet Operations

### WalletManager

Multi-chain wallet operations and ERC20 token support.

```python
from wallet.wallet_integration import WalletManager

wallet = WalletManager(default_network="ethereum")
```

#### WalletManager Methods

##### `get_wallet_info(address)`

Get comprehensive wallet information.

```python
info = wallet.get_wallet_info("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

print(f"Balance: {info.balance} ETH")
print(f"Tokens: {len(info.tokens)}")
```

**Returns:** `WalletInfo` dataclass with:

- `address: str`
- `balance: Decimal`
- `network: str`
- `tokens: List[TokenInfo]`
- `nonce: int`

---

##### `get_native_balance(address, network=None)`

Get native currency balance.

```python
balance = wallet.get_native_balance(
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    network="polygon"
)
# Returns: Decimal("1.5")
```

**Returns:** `Decimal` - Balance in native currency units

---

##### `get_token_balance(address, token_address, network=None)`

Get ERC20 token balance.

```python
usdc_balance = wallet.get_token_balance(
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
)
```

**Returns:** `TokenInfo` dataclass with:

- `address: str`
- `symbol: str`
- `name: str`
- `decimals: int`
- `balance: Decimal`
- `price_usd: Decimal | None`

---

##### `transfer_native(to_address, amount, private_key)`

Send native currency.

```python
result = wallet.transfer_native(
    to_address="0xRecipient...",
    amount=Decimal("0.1"),
    private_key="0x..."
)
```

**Returns:** `dict` with tx_hash, success, gas_used

---

##### `transfer_token(token_address, to_address, amount, private_key)`

Send ERC20 tokens.

```python
result = wallet.transfer_token(
    token_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    to_address="0xRecipient...",
    amount=Decimal("100"),
    private_key="0x..."
)
```

---

##### `validate_address(address)`

Validate an Ethereum address.

```python
is_valid = wallet.validate_address("0x742d35Cc...")
# Returns: True
```

---

##### `resolve_ens(ens_name)`

Resolve ENS name to address.

```python
address = wallet.resolve_ens("vitalik.eth")
# Returns: "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
```

---

## Real-Time Services

### WebSocketManager

Manage WebSocket connections for real-time data.

```python
from realtime.websocket_handler import WebSocketManager

ws_manager = WebSocketManager()
```

#### WebSocketManager Methods

##### `connect(uri)`

Establish WebSocket connection.

```python
await ws_manager.connect("wss://stream.binance.com:9443/ws")
```

---

##### `subscribe(channel, callback)`

Subscribe to a data channel.

```python
def handle_price(data):
    print(f"Price: {data['price']}")

await ws_manager.subscribe("btcusdt@trade", handle_price)
```

---

##### `broadcast(message)`

Send message to all connected clients.

```python
await ws_manager.broadcast({
    "type": "price_update",
    "symbol": "ETH",
    "price": "2000.50"
})
```

---

### PriceFeed

Real-time cryptocurrency prices.

```python
from realtime.price_feed import PriceFeed

feed = PriceFeed()
```

#### PriceFeed Methods

##### `get_price(symbol)`

Get current price.

```python
price = await feed.get_price("ETH")
# Returns: Decimal("2000.50")
```

---

##### `subscribe_price(symbol, callback)`

Subscribe to price updates.

```python
def on_price(symbol, price):
    print(f"{symbol}: ${price}")

feed.subscribe_price("ETH", on_price)
```

---

##### `get_price_history(symbol, interval, limit)`

Get historical prices.

```python
history = await feed.get_price_history(
    symbol="ETH",
    interval="1h",
    limit=100
)
```

---

### TransactionMonitor

Monitor blockchain transactions.

```python
from realtime.transaction_monitor import TransactionMonitor

monitor = TransactionMonitor(network="ethereum")
```

#### TransactionMonitor Methods

##### `watch_address(address, callback)`

Monitor an address for transactions.

```python
def on_transaction(tx):
    print(f"TX: {tx['hash']} - {tx['value']} ETH")

monitor.watch_address(
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    on_transaction
)
```

---

##### `watch_pending(callback)`

Monitor pending transactions.

```python
monitor.watch_pending(lambda tx: print(f"Pending: {tx['hash']}"))
```

---

## Staking & Yield

### StakingManager

Manage staking positions and yield farming.

```python
from staking.staking_manager import StakingManager

staking = StakingManager(network="ethereum")
```

#### StakingManager Methods

##### `get_pools()`

Get available staking pools.

```python
pools = staking.get_pools()

for pool in pools:
    print(f"{pool.name}: {pool.apy}% APY")
```

**Returns:** `List[PoolInfo]` with:

- `pool_address: str`
- `name: str`
- `token_address: str`
- `reward_token: str`
- `apy: Decimal`
- `total_staked: Decimal`
- `min_stake: Decimal`
- `lock_period: int`

---

##### `stake(pool_address, amount, private_key)`

Stake tokens in a pool.

```python
result = staking.stake(
    pool_address="0xPool...",
    amount=Decimal("100"),
    private_key="0x..."
)
```

**Returns:** `dict` with success, tx_hash

---

##### `unstake(pool_address, amount, private_key)`

Withdraw staked tokens.

```python
result = staking.unstake(
    pool_address="0xPool...",
    amount=Decimal("50"),
    private_key="0x..."
)
```

---

##### `claim_rewards(pool_address, private_key)`

Claim pending rewards.

```python
result = staking.claim_rewards(
    pool_address="0xPool...",
    private_key="0x..."
)
```

---

##### `get_position(pool_address, user_address)`

Get staking position.

```python
position = staking.get_position(
    "0xPool...",
    "0x742d35Cc..."
)

print(f"Staked: {position.staked_amount}")
print(f"Pending: {position.pending_rewards}")
```

**Returns:** `StakePosition` dataclass with:

- `pool_address: str`
- `user_address: str`
- `staked_amount: Decimal`
- `pending_rewards: Decimal`
- `last_stake_time: int`
- `unlock_time: int | None`

---

##### `calculate_apy(pool_address)`

Calculate current APY.

```python
apy = staking.calculate_apy("0xPool...")
print(f"Current APY: {apy}%")
```

---

## Governance

### DAOManager

Manage DAO proposals.

```python
from governance.dao_manager import DAOManager

dao = DAOManager(
    network="ethereum",
    dao_address="0xDAO..."
)
```

#### DAOManager Methods

##### `get_proposals(status=None)`

Get DAO proposals.

```python
# All proposals
proposals = dao.get_proposals()

# Active only
active = dao.get_proposals(status="active")
```

---

##### `create_proposal(title, description, actions, private_key)`

Create a new proposal.

```python
result = dao.create_proposal(
    title="Increase rewards",
    description="Proposal to increase staking rewards...",
    actions=[...],
    private_key="0x..."
)
```

---

##### `get_proposal_details(proposal_id)`

Get proposal details.

```python
details = dao.get_proposal_details(proposal_id=42)
print(f"For: {details.votes_for}")
print(f"Against: {details.votes_against}")
```

---

### VotingManager

Cast and delegate votes.

```python
from governance.voting import VotingManager

voting = VotingManager(
    network="ethereum",
    governance_address="0xGov..."
)
```

#### VotingManager Methods

##### `vote(proposal_id, support, private_key)`

Cast a vote.

```python
result = voting.vote(
    proposal_id=42,
    support=True,  # True = For, False = Against
    private_key="0x..."
)
```

---

##### `delegate(delegate_address, private_key)`

Delegate voting power.

```python
result = voting.delegate(
    delegate_address="0xDelegate...",
    private_key="0x..."
)
```

---

##### `get_voting_power(address)`

Get voting power.

```python
power = voting.get_voting_power("0x742d35Cc...")
print(f"Voting power: {power}")
```

---

## Analytics

### Data Classes

```python
from analytics.models import PortfolioSummary, TradeHistory, PerformanceMetrics
```

#### PortfolioSummary

```python
@dataclass
class PortfolioSummary:
    total_value_usd: Decimal
    tokens: List[TokenHolding]
    defi_positions: List[DeFiPosition]
    pnl_24h: Decimal
    pnl_7d: Decimal
    pnl_30d: Decimal
```

#### TradeHistory

```python
@dataclass
class TradeHistory:
    trades: List[Trade]
    total_volume: Decimal
    total_profit: Decimal
    win_rate: Decimal
```

#### PerformanceMetrics

```python
@dataclass
class PerformanceMetrics:
    roi: Decimal
    sharpe_ratio: Decimal
    max_drawdown: Decimal
    volatility: Decimal
```

---

## AI Predictions

### API Endpoint

FastAPI endpoint for market predictions.

#### `POST /predict`

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "ETH",
    "timeframe": "1h",
    "features": [2000.0, 2010.0, 1990.0, 2005.0]
  }'
```

**Request Body:**

```json
{
  "symbol": "ETH",
  "timeframe": "1h",
  "features": [2000.0, 2010.0, 1990.0, 2005.0]
}
```

**Response:**

```json
{
  "prediction": "bullish",
  "confidence": 0.75,
  "price_target": 2100.0,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Error Handling

All modules use consistent error handling:

```python
from exceptions import (
    InvalidAddressError,
    InsufficientFundsError,
    ContractError,
    NetworkError,
    AuthenticationError
)

try:
    result = wallet.transfer_native(...)
except InvalidAddressError as e:
    print(f"Invalid address: {e}")
except InsufficientFundsError as e:
    print(f"Not enough funds: {e}")
except NetworkError as e:
    print(f"Network issue: {e}")
```

---

## Supported Networks

| Network | Chain ID | Native | Testnet |
| --- | --- | --- | --- |
| ethereum | 1 | ETH | ✗ |
| goerli | 5 | ETH | ✓ |
| sepolia | 11155111 | ETH | ✓ |
| bsc | 56 | BNB | ✗ |
| polygon | 137 | MATIC | ✗ |
| arbitrum | 42161 | ETH | ✗ |
| optimism | 10 | ETH | ✗ |
| avalanche | 43114 | AVAX | ✗ |
| fantom | 250 | FTM | ✗ |
| base | 8453 | ETH | ✗ |
