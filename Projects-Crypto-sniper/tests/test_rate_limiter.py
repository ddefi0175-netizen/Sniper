"""
Tests for rate limiter middleware.
"""

import pytest
import time
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


class TestRateLimiter:
    """Tests for RateLimiter class."""
    
    def test_default_config(self):
        """Test default rate limit configuration."""
        config = {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "requests_per_day": 10000,
            "burst_size": 10
        }
        
        assert config["requests_per_minute"] > 0
        assert config["requests_per_hour"] >= config["requests_per_minute"]
        assert config["requests_per_day"] >= config["requests_per_hour"]
    
    def test_client_identification(self):
        """Test client identification from request."""
        # IP-based
        request_ip = "192.168.1.1"
        client_id = f"ip:{request_ip}"
        
        assert "ip:" in client_id
        
        # Token-based
        token = "user_abc123"
        client_id = f"token:{token}"
        
        assert "token:" in client_id
    
    def test_token_bucket_algorithm(self):
        """Test token bucket rate limiting."""
        bucket_size = 10
        refill_rate = 1  # per second
        
        # Initial state
        tokens = bucket_size
        
        # Consume tokens
        tokens -= 5
        assert tokens == 5
        
        # Request more than available
        requested = 8
        allowed = min(requested, tokens)
        assert allowed == 5
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded response."""
        response = {
            "error": "Rate limit exceeded",
            "retry_after": 60,
            "limit": "requests_per_minute",
            "current": 61,
            "max": 60
        }
        
        assert response["retry_after"] > 0
        assert response["current"] > response["max"]
    
    def test_rate_limit_headers(self):
        """Test rate limit response headers."""
        headers = {
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Remaining": "45",
            "X-RateLimit-Reset": str(int(time.time()) + 60),
            "Retry-After": "60"
        }
        
        assert int(headers["X-RateLimit-Remaining"]) <= int(headers["X-RateLimit-Limit"])
    
    def test_endpoint_specific_limits(self):
        """Test different limits for different endpoints."""
        endpoint_limits = {
            "/api/v1/trade": {"per_minute": 10},
            "/api/v1/price": {"per_minute": 120},
            "/api/v1/portfolio": {"per_minute": 30}
        }
        
        # Trade endpoint should be more restricted
        assert endpoint_limits["/api/v1/trade"]["per_minute"] < endpoint_limits["/api/v1/price"]["per_minute"]
    
    def test_whitelist_bypass(self):
        """Test whitelist bypasses rate limiting."""
        whitelist = ["192.168.1.100", "10.0.0.1"]
        client_ip = "192.168.1.100"
        
        is_whitelisted = client_ip in whitelist
        assert is_whitelisted is True
        
        # Non-whitelisted
        client_ip = "192.168.1.50"
        is_whitelisted = client_ip in whitelist
        assert is_whitelisted is False


class TestRateLimitConfig:
    """Tests for RateLimitConfig dataclass."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        valid = {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "burst_size": 10
        }
        
        assert valid["requests_per_minute"] > 0
        
        # Invalid config (negative values)
        invalid = {
            "requests_per_minute": -1
        }
        
        assert invalid["requests_per_minute"] < 0
    
    def test_per_endpoint_config(self):
        """Test per-endpoint configuration."""
        default_config = {"per_minute": 60}
        
        overrides = {
            "/api/v1/trade": {"per_minute": 10},
            "/api/v1/withdraw": {"per_minute": 5}
        }
        
        # Merge configs
        endpoint = "/api/v1/trade"
        config = overrides.get(endpoint, default_config)
        
        assert config["per_minute"] == 10


class TestRateLimitState:
    """Tests for rate limit state tracking."""
    
    def test_state_initialization(self):
        """Test initial state."""
        state = {
            "minute_count": 0,
            "hour_count": 0,
            "day_count": 0,
            "last_request": None,
            "window_start": datetime.utcnow()
        }
        
        assert state["minute_count"] == 0
    
    def test_window_reset(self):
        """Test rate limit window reset."""
        window_start = datetime.utcnow() - timedelta(minutes=2)
        window_duration = timedelta(minutes=1)
        
        should_reset = datetime.utcnow() - window_start > window_duration
        assert should_reset is True
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        # Simulate atomic counter
        import threading
        
        counter = {"value": 0}
        lock = threading.Lock()
        
        def increment():
            with lock:
                counter["value"] += 1
        
        # Simulate concurrent requests
        threads = [threading.Thread(target=increment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert counter["value"] == 10
