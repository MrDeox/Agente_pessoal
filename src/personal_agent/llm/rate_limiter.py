"""
Rate Limiter for LLM Integration

This module contains the rate limiter implementation to prevent exceeding API rate limits.
"""

import time
from collections import deque
from ..config.constants import RATE_LIMIT


class RateLimiter:
    """Rate limiter to control the frequency of API calls."""
    
    def __init__(self, max_requests: int = RATE_LIMIT.DEFAULT_REQUESTS_PER_MINUTE, period: int = RATE_LIMIT.DEFAULT_RATE_LIMIT_PERIOD):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed in the period
            period (int): Time period in seconds
        """
        self.max_requests = max_requests
        self.period = period
        self.requests = deque()
    
    def wait_if_needed(self):
        """
        Wait if rate limit would be exceeded.
        
        This method blocks until a request can be made without exceeding the rate limit.
        """
        now = time.time()
        
        # Remove old requests outside the period
        while self.requests and self.requests[0] <= now - self.period:
            self.requests.popleft()
        
        # Check if we're at the limit
        if len(self.requests) >= self.max_requests:
            sleep_time = self.period - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Record this request
        self.requests.append(now)