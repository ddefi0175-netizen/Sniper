#!/usr/bin/env python3
"""
Health check script for monitoring.

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --url http://localhost:8000
"""

import argparse
import sys
import time
from typing import Dict, Any

import requests


def check_api_health(base_url: str) -> Dict[str, Any]:
    """Check API health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "status_code": response.status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "unreachable",
            "error": str(e)
        }


def check_database(db_url: str) -> Dict[str, Any]:
    """Check database connectivity."""
    try:
        import psycopg2
        conn = psycopg2.connect(db_url, connect_timeout=5)
        cursor = conn.cursor()
        
        start = time.time()
        cursor.execute("SELECT 1")
        elapsed = (time.time() - start) * 1000
        
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "response_time_ms": elapsed
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def check_redis(redis_url: str) -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        import redis
        r = redis.from_url(redis_url, socket_timeout=5)
        
        start = time.time()
        r.ping()
        elapsed = (time.time() - start) * 1000
        
        return {
            "status": "healthy",
            "response_time_ms": elapsed
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def check_blockchain(network: str) -> Dict[str, Any]:
    """Check blockchain RPC connectivity."""
    try:
        from web3 import Web3
        from config.networks import get_network_config
        
        config = get_network_config(network)
        w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        
        start = time.time()
        block = w3.eth.block_number
        elapsed = (time.time() - start) * 1000
        
        return {
            "status": "healthy",
            "network": network,
            "block_number": block,
            "response_time_ms": elapsed
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "network": network,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Health check script")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checks": {}
    }
    
    # Check API
    print("🔍 Checking API health...")
    api_result = check_api_health(args.url)
    results["checks"]["api"] = api_result
    
    if api_result["status"] == "healthy":
        print(f"   ✓ API is healthy ({api_result['response_time_ms']:.1f}ms)")
    else:
        print(f"   ✗ API is {api_result['status']}")
    
    # Check Database
    db_url = os.getenv("DATABASE_URL")
    if db_url and "postgresql" in db_url:
        print("🔍 Checking database...")
        db_result = check_database(db_url)
        results["checks"]["database"] = db_result
        
        if db_result["status"] == "healthy":
            print(f"   ✓ Database is healthy ({db_result['response_time_ms']:.1f}ms)")
        else:
            print(f"   ✗ Database is {db_result['status']}")
    
    # Check Redis
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        print("🔍 Checking Redis...")
        redis_result = check_redis(redis_url)
        results["checks"]["redis"] = redis_result
        
        if redis_result["status"] == "healthy":
            print(f"   ✓ Redis is healthy ({redis_result['response_time_ms']:.1f}ms)")
        else:
            print(f"   ✗ Redis is {redis_result['status']}")
    
    # Check Blockchain
    print("🔍 Checking blockchain RPC...")
    for network in ["ethereum", "polygon"]:
        try:
            rpc_result = check_blockchain(network)
            results["checks"][f"rpc_{network}"] = rpc_result
            
            if rpc_result["status"] == "healthy":
                print(f"   ✓ {network.capitalize()} RPC is healthy (block {rpc_result['block_number']})")
            else:
                print(f"   ✗ {network.capitalize()} RPC is {rpc_result['status']}")
        except Exception:
            pass
    
    # Summary
    all_healthy = all(
        c.get("status") == "healthy" 
        for c in results["checks"].values()
    )
    
    results["overall"] = "healthy" if all_healthy else "degraded"
    
    print()
    if all_healthy:
        print("✓ All systems operational")
    else:
        print("⚠ Some systems are degraded")
    
    if args.json:
        import json
        print()
        print(json.dumps(results, indent=2))
    
    sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    main()
