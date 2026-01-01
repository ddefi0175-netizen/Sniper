#!/usr/bin/env python3
"""
Deploy contract script.

Usage:
    python scripts/deploy_contract.py --network sepolia --contract MyContract
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_contract_abi(contract_name: str) -> dict:
    """Load contract ABI from file."""
    abi_path = project_root / "contracts" / "abi" / f"{contract_name}.json"
    
    if not abi_path.exists():
        raise FileNotFoundError(f"ABI not found: {abi_path}")
    
    with open(abi_path) as f:
        return json.load(f)


def deploy_contract(network: str, contract_name: str, constructor_args: list = None):
    """Deploy a contract to the specified network."""
    from web3 import Web3
    from config.networks import get_network_config
    
    # Load configuration
    config = get_network_config(network)
    
    if not config.is_testnet:
        confirm = input(f"⚠ You are deploying to MAINNET ({network}). Continue? [y/N]: ")
        if confirm.lower() != 'y':
            print("Deployment cancelled.")
            return
    
    # Get private key
    private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    if not private_key:
        print("✗ DEPLOYER_PRIVATE_KEY not set in environment")
        sys.exit(1)
    
    # Connect to network
    print(f"📡 Connecting to {network}...")
    w3 = Web3(Web3.HTTPProvider(config.rpc_url))
    
    if not w3.is_connected():
        print(f"✗ Failed to connect to {network}")
        sys.exit(1)
    
    print(f"✓ Connected to {network} (Chain ID: {w3.eth.chain_id})")
    
    # Load account
    account = w3.eth.account.from_key(private_key)
    print(f"📍 Deployer address: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"💰 Balance: {balance_eth} {config.native_symbol}")
    
    if balance == 0:
        print("✗ Deployer has no balance")
        sys.exit(1)
    
    # Load contract
    print(f"📄 Loading contract: {contract_name}")
    contract_data = load_contract_abi(contract_name)
    
    abi = contract_data.get("abi")
    bytecode = contract_data.get("bytecode")
    
    if not bytecode:
        print("✗ Contract bytecode not found in ABI file")
        sys.exit(1)
    
    # Deploy
    print("🚀 Deploying contract...")
    
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build constructor transaction
    if constructor_args:
        tx = contract.constructor(*constructor_args)
    else:
        tx = contract.constructor()
    
    # Estimate gas
    gas_estimate = tx.estimate_gas({'from': account.address})
    gas_price = w3.eth.gas_price
    
    print(f"⛽ Estimated gas: {gas_estimate}")
    print(f"💸 Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")
    
    # Build and sign transaction
    tx_dict = tx.build_transaction({
        'from': account.address,
        'gas': int(gas_estimate * 1.2),
        'gasPrice': gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': w3.eth.chain_id
    })
    
    signed = account.sign_transaction(tx_dict)
    
    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"📤 Transaction sent: {tx_hash.hex()}")
    print(f"   Explorer: {config.explorer_url}/tx/{tx_hash.hex()}")
    
    # Wait for receipt
    print("⏳ Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    if receipt['status'] == 1:
        print(f"✓ Contract deployed successfully!")
        print(f"📍 Contract address: {receipt['contractAddress']}")
        print(f"⛽ Gas used: {receipt['gasUsed']}")
        
        # Save deployment info
        deployment_info = {
            "network": network,
            "contract": contract_name,
            "address": receipt['contractAddress'],
            "tx_hash": tx_hash.hex(),
            "deployer": account.address,
            "block_number": receipt['blockNumber'],
            "gas_used": receipt['gasUsed']
        }
        
        deployments_dir = project_root / "deployments"
        deployments_dir.mkdir(exist_ok=True)
        
        deployment_file = deployments_dir / f"{contract_name}_{network}.json"
        with open(deployment_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"📝 Deployment info saved to: {deployment_file}")
        
    else:
        print("✗ Deployment failed!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Deploy smart contract")
    parser.add_argument("--network", required=True, help="Target network (e.g., sepolia, ethereum)")
    parser.add_argument("--contract", required=True, help="Contract name to deploy")
    parser.add_argument("--args", nargs="*", help="Constructor arguments")
    
    args = parser.parse_args()
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
    
    deploy_contract(args.network, args.contract, args.args)


if __name__ == "__main__":
    main()
