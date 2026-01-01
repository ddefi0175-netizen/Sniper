#!/usr/bin/env python3
"""
Development server startup script.
"""

import os
import sys
import uvicorn


def main():
    """Start the development server."""
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # Load environment variables
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✓ Loaded environment from {env_file}")
    else:
        print("⚠ No .env file found, using system environment")
    
    # Check required environment variables
    required_vars = ["INFURA_API_KEY", "JWT_SECRET_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"✗ Missing required environment variables: {', '.join(missing)}")
        print("  Copy .env.example to .env and fill in your values")
        sys.exit(1)
    
    print("✓ Environment configured")
    
    # Configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🚀 Starting Crypto Sniper API at http://{host}:{port}")
    print(f"   Reload: {reload}")
    print(f"   Docs: http://{host}:{port}/docs")
    print()
    
    # Start server
    uvicorn.run(
        "backend.ai_predict:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
