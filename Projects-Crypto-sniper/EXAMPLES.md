# Examples

Practical examples for using Crypto Sniper.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Reading Blockchain Data](#reading-blockchain-data)
- [Token Operations](#token-operations)
- [Staking](#staking)
- [Governance](#governance)
- [Real-Time Monitoring](#real-time-monitoring)
- [Multi-Chain Operations](#multi-chain-operations)

---

## Quick Start

### Basic Setup

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify configuration
assert os.getenv("INFURA_API_KEY"), "Missing INFURA_API_KEY"
assert os.getenv("JWT_SECRET_KEY"), "Missing JWT_SECRET_KEY"

print("✅ Configuration loaded")
```

### Connect to Network

```python
from config.networks import get_network_config

# Get Ethereum mainnet config
eth_config = get_network_config("ethereum")
print(f"Network: {eth_config.name}")
print(f"Chain ID: {eth_config.chain_id}")
print(f"RPC: {eth_config.rpc_url}")

# Use testnet for development
sepolia_config = get_network_config("sepolia")
print(f"Testnet: {sepolia_config.is_testnet}")
```

---

## Authentication

### Web3 Wallet Login

```python
from auth.wallet_auth import WalletAuthenticator

auth = WalletAuthenticator()

# Step 1: Generate nonce for user
nonce = auth.generate_nonce()
message = f"Sign this message to login: {nonce}"
print(f"Message to sign: {message}")

# Step 2: User signs message in their wallet (frontend)
# signature = "0x..." (from wallet)

# Step 3: Verify signature
wallet_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
signature = "0x..."  # From user's wallet

if auth.verify_signature(wallet_address, message, signature):
    # Step 4: Create session token
    token = auth.create_token(wallet_address)
    print(f"JWT Token: {token}")
else:
    print("Invalid signature!")
```

### Verify Session Token

```python
# On subsequent requests
token = "eyJhbGciOiJIUzI1NiIs..."

result = auth.verify_token(token)

if result.authenticated:
    print(f"Authenticated wallet: {result.wallet_address}")
    print(f"Token expires: {result.expires_at}")
else:
    print(f"Authentication failed: {result.error}")
```

---

## Reading Blockchain Data

### Get Wallet Balance

```python
from wallet.wallet_integration import WalletManager
from decimal import Decimal

wallet = WalletManager(default_network="ethereum")

address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

# Native balance
eth_balance = wallet.get_native_balance(address)
print(f"ETH Balance: {eth_balance}")

# On different network
matic_balance = wallet.get_native_balance(address, network="polygon")
print(f"MATIC Balance: {matic_balance}")
```

### Get Token Balance

```python
# USDC on Ethereum
usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

token_info = wallet.get_token_balance(address, usdc_address)

print(f"Token: {token_info.name} ({token_info.symbol})")
print(f"Balance: {token_info.balance}")
print(f"Decimals: {token_info.decimals}")
```

### Get Full Wallet Info

```python
info = wallet.get_wallet_info(address)

print(f"Address: {info.address}")
print(f"Network: {info.network}")
print(f"Native Balance: {info.balance}")
print(f"Nonce: {info.nonce}")
print(f"Tokens: {len(info.tokens)}")

for token in info.tokens:
    print(f"  - {token.symbol}: {token.balance}")
```

---

## Token Operations

### Read Token Contract

```python
from contracts.smart_contract import SmartContractManager

# Standard ERC20 ABI (minimal)
ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
]

manager = SmartContractManager(network="ethereum")
usdc = manager.load_contract(usdc_address, ERC20_ABI)

# Read token info
name = manager.read_contract(usdc, "name")
symbol = manager.read_contract(usdc, "symbol")
decimals = manager.read_contract(usdc, "decimals")
total_supply = manager.read_contract(usdc, "totalSupply")

print(f"Token: {name} ({symbol})")
print(f"Decimals: {decimals}")
print(f"Total Supply: {total_supply / (10 ** decimals):,.2f}")
```

### Transfer Tokens

```python
import os

# ⚠️ Use testnet for testing!
manager = SmartContractManager(
    network="sepolia",  # Testnet!
    private_key=os.getenv("WALLET_PRIVATE_KEY")
)

# Add transfer function to ABI
TRANSFER_ABI = [
    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
]

token = manager.load_contract(token_address, ERC20_ABI + TRANSFER_ABI)

# Calculate amount with decimals
amount = int(Decimal("100") * Decimal(10 ** 18))

# Estimate gas first
gas = manager.estimate_gas(token, "transfer", recipient, amount)
print(f"Estimated gas: {gas}")

# Execute transfer
result = manager.write_contract(
    token,
    "transfer",
    recipient,
    amount,
    gas_limit=gas + 10000  # Add buffer
)

if result.success:
    print(f"Transfer successful!")
    print(f"TX Hash: {result.tx_hash}")
    print(f"Block: {result.block_number}")
    print(f"Gas Used: {result.gas_used}")
else:
    print(f"Transfer failed: {result.error}")
```

---

## Staking

### View Available Pools

```python
from staking.staking_manager import StakingManager

staking = StakingManager(network="ethereum")

pools = staking.get_pools()

print("Available Staking Pools:")
print("-" * 60)

for pool in pools:
    print(f"Pool: {pool.name}")
    print(f"  Address: {pool.pool_address}")
    print(f"  APY: {pool.apy}%")
    print(f"  Total Staked: {pool.total_staked:,.2f}")
    print(f"  Min Stake: {pool.min_stake}")
    print(f"  Lock Period: {pool.lock_period} days")
    print()
```

### Check Your Position

```python
user_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
pool_address = "0xPool..."

position = staking.get_position(pool_address, user_address)

print(f"Your Staking Position:")
print(f"  Staked: {position.staked_amount}")
print(f"  Pending Rewards: {position.pending_rewards}")
print(f"  Last Stake: {position.last_stake_time}")
if position.unlock_time:
    print(f"  Unlocks: {position.unlock_time}")
```

### Stake Tokens

```python
import os

staking = StakingManager(network="sepolia")  # Testnet!

result = staking.stake(
    pool_address="0xPool...",
    amount=Decimal("100"),
    private_key=os.getenv("WALLET_PRIVATE_KEY")
)

if result["success"]:
    print(f"Staked successfully! TX: {result['tx_hash']}")
else:
    print(f"Staking failed: {result['error']}")
```

### Claim Rewards

```python
result = staking.claim_rewards(
    pool_address="0xPool...",
    private_key=os.getenv("WALLET_PRIVATE_KEY")
)

if result["success"]:
    print(f"Rewards claimed! TX: {result['tx_hash']}")
```

---

## Governance

### View Proposals

```python
from governance.dao_manager import DAOManager

dao = DAOManager(
    network="ethereum",
    dao_address="0xDAO..."
)

# Get all active proposals
proposals = dao.get_proposals(status="active")

print("Active Proposals:")
print("-" * 60)

for prop in proposals:
    print(f"#{prop.id}: {prop.title}")
    print(f"  Status: {prop.status}")
    print(f"  For: {prop.votes_for} | Against: {prop.votes_against}")
    print(f"  Ends: {prop.end_time}")
    print()
```

### Vote on Proposal

```python
from governance.voting import VotingManager
import os

voting = VotingManager(
    network="ethereum",
    governance_address="0xGov..."
)

# Check voting power
my_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
power = voting.get_voting_power(my_address)
print(f"Your voting power: {power}")

# Cast vote
if power > 0:
    result = voting.vote(
        proposal_id=42,
        support=True,  # Vote FOR
        private_key=os.getenv("WALLET_PRIVATE_KEY")
    )
    print(f"Vote cast! TX: {result['tx_hash']}")
```

### Delegate Votes

```python
# Delegate your voting power
result = voting.delegate(
    delegate_address="0xDelegate...",
    private_key=os.getenv("WALLET_PRIVATE_KEY")
)

print(f"Delegated! TX: {result['tx_hash']}")
```

---

## Real-Time Monitoring

### Price Feed

```python
import asyncio
from realtime.price_feed import PriceFeed

async def main():
    feed = PriceFeed()
    
    # Get current price
    eth_price = await feed.get_price("ETH")
    print(f"ETH Price: ${eth_price}")
    
    # Subscribe to updates
    def on_price_update(symbol, price):
        print(f"{symbol}: ${price}")
    
    feed.subscribe_price("ETH", on_price_update)
    feed.subscribe_price("BTC", on_price_update)
    
    # Keep running
    await asyncio.sleep(60)

asyncio.run(main())
```

### Transaction Monitor

```python
import asyncio
from realtime.transaction_monitor import TransactionMonitor

monitor = TransactionMonitor(network="ethereum")

def on_transaction(tx):
    print(f"New TX: {tx['hash']}")
    print(f"  From: {tx['from']}")
    print(f"  To: {tx['to']}")
    print(f"  Value: {tx['value']} ETH")

# Watch specific address
monitor.watch_address(
    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    on_transaction
)

# Keep monitoring
asyncio.get_event_loop().run_forever()
```

### Contract Events

```python
manager = SmartContractManager(network="ethereum")
usdc = manager.load_contract(usdc_address, ERC20_ABI)

def on_transfer(event):
    args = event['args']
    print(f"Transfer: {args['from']} -> {args['to']}: {args['value']}")

# Subscribe to Transfer events
manager.subscribe_events(usdc, "Transfer", on_transfer)
```

---

## Multi-Chain Operations

### Check Balance Across Chains

```python
from wallet.wallet_integration import WalletManager

address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

networks = ["ethereum", "polygon", "arbitrum", "optimism", "base"]

print(f"Balances for {address}")
print("-" * 50)

for network in networks:
    wallet = WalletManager(default_network=network)
    balance = wallet.get_native_balance(address)
    symbol = get_network_config(network).native_currency
    print(f"{network}: {balance} {symbol}")
```

### Multi-Chain Token Check

```python
# USDC addresses on different chains
USDC_ADDRESSES = {
    "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "polygon": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "arbitrum": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
    "optimism": "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
}

address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

print(f"USDC Balances for {address}")
print("-" * 50)

for network, usdc_addr in USDC_ADDRESSES.items():
    wallet = WalletManager(default_network=network)
    token = wallet.get_token_balance(address, usdc_addr)
    print(f"{network}: {token.balance} USDC")
```

---

## Error Handling

### Robust Transaction Handling

```python
from exceptions import (
    InvalidAddressError,
    InsufficientFundsError,
    ContractError,
    NetworkError
)

def safe_transfer(wallet, to_address, amount, private_key):
    """Transfer with comprehensive error handling."""
    try:
        # Validate address
        if not wallet.validate_address(to_address):
            raise InvalidAddressError(f"Invalid address: {to_address}")
        
        # Check balance
        balance = wallet.get_native_balance(wallet.address)
        if balance < amount:
            raise InsufficientFundsError(
                f"Need {amount}, have {balance}"
            )
        
        # Execute transfer
        result = wallet.transfer_native(to_address, amount, private_key)
        
        if result["success"]:
            return {"success": True, "tx_hash": result["tx_hash"]}
        else:
            raise ContractError(result.get("error", "Unknown error"))
            
    except InvalidAddressError as e:
        return {"success": False, "error": f"Invalid address: {e}"}
    except InsufficientFundsError as e:
        return {"success": False, "error": f"Insufficient funds: {e}"}
    except ContractError as e:
        return {"success": False, "error": f"Contract error: {e}"}
    except NetworkError as e:
        return {"success": False, "error": f"Network error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}
```

---

## Next Steps

1. **Read the full [API Reference](API.md)**
2. **Review [Security Guidelines](SECURITY.md)**
3. **Join our community on Discord**
4. **Report issues on GitHub**
