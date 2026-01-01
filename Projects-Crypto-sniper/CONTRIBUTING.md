# Contributing to Crypto Sniper

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A code editor (VS Code recommended)

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/crypto-sniper.git
   cd crypto-sniper
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies**

   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**

   ```bash
   pre-commit install
   ```

5. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your test API keys
   ```

---

## 📝 Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these tools:

- **Black** for formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Run Formatters

```bash
# Format code
black .
isort .

# Check linting
flake8 .

# Type checking
mypy .
```

### Naming Conventions

```python
# Classes: PascalCase
class WalletManager:
    pass

# Functions/methods: snake_case
def get_wallet_info():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

### Type Hints

All public functions must have type hints:

```python
def get_balance(address: str, network: str = "ethereum") -> Decimal:
    """Get wallet balance."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def transfer_tokens(
    to_address: str,
    amount: Decimal,
    token_address: str
) -> Dict[str, Any]:
    """
    Transfer ERC20 tokens to an address.

    Args:
        to_address: Recipient wallet address
        amount: Amount to transfer
        token_address: ERC20 token contract address

    Returns:
        Dictionary containing:
            - success: Whether transfer succeeded
            - tx_hash: Transaction hash
            - gas_used: Gas consumed

    Raises:
        ValueError: If address is invalid
        InsufficientFundsError: If balance too low

    Example:
        >>> result = transfer_tokens("0x...", Decimal("100"), "0x...")
        >>> print(result['tx_hash'])
    """
    pass
```

---

## 🔀 Git Workflow

### Branch Naming

```text
feat/add-nft-support       # New feature
fix/wallet-balance-bug     # Bug fix
docs/update-readme         # Documentation
refactor/optimize-queries  # Code refactoring
test/add-staking-tests     # Test additions
chore/update-deps          # Maintenance
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**

```bash
git commit -m "feat(staking): add compound rewards function"
git commit -m "fix(wallet): correct ENS resolution for subdomains"
git commit -m "docs(api): add examples for governance module"
```

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific module
pytest tests/test_wallet.py -v

# Specific test
pytest tests/test_wallet.py::test_get_balance -v
```

### Writing Tests

```python
import pytest
from decimal import Decimal
from wallet.wallet_integration import WalletManager

class TestWalletManager:
    """Tests for WalletManager class."""

    @pytest.fixture
    def wallet_manager(self):
        """Create WalletManager instance."""
        return WalletManager(default_network="sepolia")

    def test_validate_address_valid(self, wallet_manager):
        """Test validation with valid address."""
        address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        assert wallet_manager.validate_address(address) is True

    def test_validate_address_invalid(self, wallet_manager):
        """Test validation with invalid address."""
        assert wallet_manager.validate_address("invalid") is False

    @pytest.mark.asyncio
    async def test_get_balance(self, wallet_manager):
        """Test balance retrieval."""
        balance = await wallet_manager.get_native_balance(
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        )
        assert isinstance(balance, Decimal)
        assert balance >= 0
```

### Test Requirements

- All new features must have tests
- Maintain >80% code coverage
- Use pytest fixtures for setup
- Mock external API calls
- Test edge cases and errors

---

## 📦 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with `main`

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe tests performed

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No sensitive data committed
```

### Review Process

1. Create PR from your branch to `main`
2. Fill out PR template
3. Request review from maintainers
4. Address review feedback
5. Squash and merge when approved

---

## 🔒 Security

### Sensitive Data

**NEVER commit:**

- API keys
- Private keys
- Passwords
- `.env` files

### Reporting Vulnerabilities

1. **DO NOT** open a public issue
2. Email: <security@example.com>
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## 📋 Issue Guidelines

### Bug Reports

```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
1. Step one
2. Step two
3. See error

**Expected behavior**
What should happen

**Environment**
- OS: Windows 11
- Python: 3.10.5
- Package versions: ...

**Additional context**
Any other relevant info
```

### Feature Requests

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired feature

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Any other relevant info
```

---

## 🎯 Development Priorities

### High Priority

- Security fixes
- Breaking bug fixes
- Core functionality

### Medium Priority

- New features
- Performance improvements
- Documentation

### Low Priority

- Code style improvements
- Minor enhancements

---

## 📞 Contact

- **Discord**: [Join our server](https://discord.gg/cryptosniper)
- **Email**: <contributors@example.com>
- **GitHub Discussions**: For questions and ideas

---

Thank you for contributing! 🙏
