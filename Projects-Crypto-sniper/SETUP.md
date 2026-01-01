# Setup and Installation Guide

Complete guide for setting up Crypto Sniper in various environments.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Install](#quick-install)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Docker Setup](#docker-setup)
- [Environment Configuration](#environment-configuration)
- [Network Configuration](#network-configuration)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **Python**: 3.10 or higher
- **RAM**: 4GB
- **Storage**: 1GB free space
- **Network**: Stable internet connection

### Recommended

- **Python**: 3.11+
- **RAM**: 8GB+
- **SSD**: For better performance

---

## Quick Install

### 1. Clone Repository

```bash
git clone https://github.com/your-org/crypto-sniper.git
cd crypto-sniper
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Run

```bash
python -m uvicorn backend.ai_predict:app --reload
```

---

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- VS Code (recommended)
- Node.js (for frontend, if applicable)

### Step-by-Step

#### 1. Fork and Clone

```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/crypto-sniper.git
cd crypto-sniper
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Dev Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs:

- Core dependencies (web3, fastapi, etc.)
- Testing tools (pytest, coverage)
- Linting tools (black, flake8, mypy)
- Documentation tools (mkdocs)

#### 4. Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

#### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required
INFURA_API_KEY=your_infura_api_key
ALCHEMY_API_KEY=your_alchemy_api_key
JWT_SECRET_KEY=your_secret_key_min_32_characters

# Development Database
DATABASE_URL=sqlite:///./dev.db
REDIS_URL=redis://localhost:6379/0

# Optional (for testing)
ETHERSCAN_API_KEY=your_etherscan_key
```

#### 6. Verify Installation

```bash
# Run tests
pytest

# Check linting
flake8 .

# Type checking
mypy .
```

#### 7. Run Development Server

```bash
uvicorn backend.ai_predict:app --reload --port 8000
```

---

## Production Setup

### Prerequisites

- Ubuntu 20.04+ or similar
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Nginx (for reverse proxy)
- SSL certificate

### Step-by-Step

#### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.10 python3.10-venv python3-pip git nginx redis-server postgresql -y
```

#### 2. Create Application User

```bash
sudo useradd -m -s /bin/bash cryptosniper
sudo su - cryptosniper
```

#### 3. Clone and Setup

```bash
git clone https://github.com/your-org/crypto-sniper.git
cd crypto-sniper

python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

#### 4. Database Setup

```bash
# PostgreSQL
sudo -u postgres createuser cryptosniper
sudo -u postgres createdb cryptosniper_db -O cryptosniper
sudo -u postgres psql -c "ALTER USER cryptosniper WITH PASSWORD 'secure_password';"
```

#### 5. Configure Environment

```bash
nano .env
```

```env
# Production settings
DEBUG=False
ENVIRONMENT=production

# API Keys
INFURA_API_KEY=your_production_infura_key
ALCHEMY_API_KEY=your_production_alchemy_key

# Security
JWT_SECRET_KEY=very_long_random_string_at_least_64_characters

# Database
DATABASE_URL=postgresql://cryptosniper:secure_password@localhost:5432/cryptosniper_db

# Redis
REDIS_URL=redis://localhost:6379/0
```

#### 6. Systemd Service

Create `/etc/systemd/system/cryptosniper.service`:

```ini
[Unit]
Description=Crypto Sniper API
After=network.target postgresql.service redis.service

[Service]
User=cryptosniper
Group=cryptosniper
WorkingDirectory=/home/cryptosniper/crypto-sniper
Environment="PATH=/home/cryptosniper/crypto-sniper/.venv/bin"
ExecStart=/home/cryptosniper/crypto-sniper/.venv/bin/gunicorn backend.ai_predict:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cryptosniper
sudo systemctl start cryptosniper
```

#### 7. Nginx Configuration

Create `/etc/nginx/sites-available/cryptosniper`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/cryptosniper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Docker Setup

### Using Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://crypto:crypto@db:5432/cryptosniper
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: crypto
      POSTGRES_PASSWORD: crypto
      POSTGRES_DB: cryptosniper
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "backend.ai_predict:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

Run:

```bash
docker-compose up -d
```

### Docker Only

```bash
# Build
docker build -t crypto-sniper .

# Run
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name crypto-sniper \
  crypto-sniper
```

---

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `INFURA_API_KEY` | Infura API key | `abc123...` |
| `ALCHEMY_API_KEY` | Alchemy API key | `xyz789...` |
| `JWT_SECRET_KEY` | JWT signing secret (32+ chars) | `your_secure_random_key` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection | `sqlite:///./app.db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `DEBUG` | Enable debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ETHERSCAN_API_KEY` | Etherscan API | - |
| `COINGECKO_API_KEY` | CoinGecko API | - |

### Getting API Keys

#### Infura

1. Go to [infura.io](https://infura.io)
2. Create account
3. Create new project
4. Copy Project ID

#### Alchemy

1. Go to [alchemy.com](https://alchemy.com)
2. Create account
3. Create new app
4. Copy API key

---

## Network Configuration

### Supported Networks

Default networks are configured in `config/networks.py`:

| Network | Chain ID | Type |
|---------|----------|------|
| ethereum | 1 | Mainnet |
| goerli | 5 | Testnet |
| sepolia | 11155111 | Testnet |
| bsc | 56 | Mainnet |
| polygon | 137 | Mainnet |
| arbitrum | 42161 | L2 |
| optimism | 10 | L2 |
| avalanche | 43114 | Mainnet |
| fantom | 250 | Mainnet |
| base | 8453 | L2 |

### Custom Network

Add to `config/networks.py`:

```python
NetworkConfig(
    name="custom_network",
    chain_id=12345,
    rpc_url="https://rpc.custom-network.com",
    native_currency="CUSTOM",
    explorer_url="https://explorer.custom-network.com",
    is_testnet=False
)
```

---

## Troubleshooting

### Common Issues

#### ModuleNotFoundError

```
ModuleNotFoundError: No module named 'web3'
```

**Solution:**

```bash
pip install -r requirements.txt
```

#### Connection Error

```
ConnectionError: Could not connect to RPC
```

**Solutions:**

1. Check API key is valid
2. Check internet connection
3. Try different RPC provider

#### JWT Error

```
jwt.exceptions.InvalidSignatureError
```

**Solutions:**

1. Ensure JWT_SECRET_KEY is set
2. Use consistent key across restarts
3. Clear expired tokens

#### Import Error

```
ImportError: cannot import name 'encode_defunct'
```

**Solution:**

```bash
pip install eth-account>=0.8.0
```

### Debug Mode

Enable debug logging:

```bash
# In .env
DEBUG=True
LOG_LEVEL=DEBUG

# Or via command line
export DEBUG=True
python -m uvicorn backend.ai_predict:app --reload --log-level debug
```

### Health Check

Verify installation:

```python
# test_installation.py
def test_imports():
    """Test all critical imports."""
    from config.networks import get_network_config
    from auth.wallet_auth import WalletAuthenticator
    from contracts.smart_contract import SmartContractManager
    from wallet.wallet_integration import WalletManager
    print("✅ All imports successful")

def test_network():
    """Test network configuration."""
    from config.networks import get_network_config
    config = get_network_config("ethereum")
    assert config.chain_id == 1
    print(f"✅ Network config: {config.name}")

def test_auth():
    """Test authentication module."""
    from auth.wallet_auth import WalletAuthenticator
    auth = WalletAuthenticator()
    nonce = auth.generate_nonce()
    assert len(nonce) == 66  # 0x + 64 hex chars
    print(f"✅ Auth nonce: {nonce[:20]}...")

if __name__ == "__main__":
    test_imports()
    test_network()
    test_auth()
    print("\n🎉 Installation verified!")
```

Run:

```bash
python test_installation.py
```

---

## Next Steps

1. **Read the [Examples](EXAMPLES.md)** - Practical usage examples
2. **Review [API Reference](API.md)** - Complete API documentation
3. **Check [Security](SECURITY.md)** - Security best practices
4. **Contribute** - See [CONTRIBUTING.md](CONTRIBUTING.md)
