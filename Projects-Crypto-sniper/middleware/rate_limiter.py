"""
Rate limiting middleware for API endpoints.

Provides protection against abuse and ensures fair resource usage.
"""

import time
import logging
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from functools import wraps
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10
    cooldown_seconds: int = 60


@dataclass
class RateLimitState:
    """Track rate limit state for a client."""
    
    minute_requests: int = 0
    hour_requests: int = 0
    day_requests: int = 0
    minute_reset: float = 0
    hour_reset: float = 0
    day_reset: float = 0
    burst_tokens: float = 10
    last_request: float = 0


class RateLimiter:
    """
    Token bucket rate limiter with multiple time windows.
    
    Features:
    - Per-minute, per-hour, and per-day limits
    - Burst allowance for temporary spikes
    - Per-client tracking by IP or wallet address
    
    Example:
        limiter = RateLimiter()
        
        @limiter.limit(requests_per_minute=30)
        async def my_endpoint(request):
            ...
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self._clients: Dict[str, RateLimitState] = defaultdict(RateLimitState)
    
    def _get_client_key(self, identifier: str) -> str:
        """Get unique key for client."""
        return identifier.lower()
    
    def _refill_tokens(self, state: RateLimitState, now: float) -> None:
        """Refill burst tokens based on elapsed time."""
        elapsed = now - state.last_request
        tokens_to_add = elapsed * (self.config.burst_size / 60)  # Refill over 1 minute
        state.burst_tokens = min(
            self.config.burst_size,
            state.burst_tokens + tokens_to_add
        )
    
    def _reset_windows(self, state: RateLimitState, now: float) -> None:
        """Reset time windows if expired."""
        if now >= state.minute_reset:
            state.minute_requests = 0
            state.minute_reset = now + 60
        
        if now >= state.hour_reset:
            state.hour_requests = 0
            state.hour_reset = now + 3600
        
        if now >= state.day_reset:
            state.day_requests = 0
            state.day_reset = now + 86400
    
    def check_rate_limit(
        self,
        identifier: str,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None
    ) -> tuple[bool, Optional[str], Optional[int]]:
        """
        Check if request is within rate limits.
        
        Args:
            identifier: Client identifier (IP or wallet)
            requests_per_minute: Override per-minute limit
            requests_per_hour: Override per-hour limit
            requests_per_day: Override per-day limit
        
        Returns:
            Tuple of (allowed, error_message, retry_after_seconds)
        """
        now = time.time()
        key = self._get_client_key(identifier)
        state = self._clients[key]
        
        # Initialize reset times if needed
        if state.minute_reset == 0:
            state.minute_reset = now + 60
            state.hour_reset = now + 3600
            state.day_reset = now + 86400
            state.burst_tokens = self.config.burst_size
        
        # Reset expired windows
        self._reset_windows(state, now)
        
        # Refill burst tokens
        self._refill_tokens(state, now)
        
        # Get effective limits
        minute_limit = requests_per_minute or self.config.requests_per_minute
        hour_limit = requests_per_hour or self.config.requests_per_hour
        day_limit = requests_per_day or self.config.requests_per_day
        
        # Check limits
        if state.day_requests >= day_limit:
            retry_after = int(state.day_reset - now)
            return False, "Daily rate limit exceeded", retry_after
        
        if state.hour_requests >= hour_limit:
            retry_after = int(state.hour_reset - now)
            return False, "Hourly rate limit exceeded", retry_after
        
        if state.minute_requests >= minute_limit:
            # Allow burst if tokens available
            if state.burst_tokens >= 1:
                state.burst_tokens -= 1
            else:
                retry_after = int(state.minute_reset - now)
                return False, "Rate limit exceeded", retry_after
        
        # Request allowed - increment counters
        state.minute_requests += 1
        state.hour_requests += 1
        state.day_requests += 1
        state.last_request = now
        
        return True, None, None
    
    def get_remaining(self, identifier: str) -> Dict[str, int]:
        """
        Get remaining requests for a client.
        
        Args:
            identifier: Client identifier
        
        Returns:
            Dictionary with remaining counts per window
        """
        key = self._get_client_key(identifier)
        state = self._clients[key]
        
        return {
            "minute": max(0, self.config.requests_per_minute - state.minute_requests),
            "hour": max(0, self.config.requests_per_hour - state.hour_requests),
            "day": max(0, self.config.requests_per_day - state.day_requests),
            "burst": int(state.burst_tokens)
        }
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit state for a client."""
        key = self._get_client_key(identifier)
        if key in self._clients:
            del self._clients[key]


def rate_limit(
    limiter: RateLimiter,
    identifier_func: Callable,
    requests_per_minute: Optional[int] = None,
    requests_per_hour: Optional[int] = None
):
    """
    Decorator for rate limiting functions.
    
    Args:
        limiter: RateLimiter instance
        identifier_func: Function to extract client identifier from request
        requests_per_minute: Per-minute limit override
        requests_per_hour: Per-hour limit override
    
    Example:
        @rate_limit(limiter, lambda req: req.client.host, requests_per_minute=30)
        async def my_endpoint(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract identifier from first argument (usually request)
            identifier = identifier_func(args[0] if args else kwargs.get('request'))
            
            allowed, error, retry_after = limiter.check_rate_limit(
                identifier,
                requests_per_minute=requests_per_minute,
                requests_per_hour=requests_per_hour
            )
            
            if not allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail=error,
                    headers={"Retry-After": str(retry_after)}
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global rate limiter instance
default_limiter = RateLimiter()
