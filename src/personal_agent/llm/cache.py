"""
Cache for LLM Responses

This module contains the cache implementation for storing LLM responses with TTL.
"""

import time
import hashlib
import json
from typing import Dict, Optional, Any
from threading import Lock
from .models import LLMResponse
from ..utils.logging import get_logger


class LLmCache:
    """
    Cache for LLM responses with TTL support.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            default_ttl (int): Default time-to-live in seconds (default: 1 hour)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.logger = get_logger()
        self.logger.info(f"LLM cache initialized with default TTL: {default_ttl}s")
    
    def _generate_key(self, messages: list, **kwargs) -> str:
        """
        Generate a cache key from messages and parameters.
        
        Args:
            messages (list): List of messages
            **kwargs: Additional parameters
            
        Returns:
            str: Generated cache key
        """
        # Create a hashable representation of messages and kwargs
        key_data = {
            "messages": [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ],
            "kwargs": kwargs
        }
        
        # Generate hash
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, messages: list, **kwargs) -> Optional[LLMResponse]:
        """
        Get a cached response.
        
        Args:
            messages (list): List of messages
            **kwargs: Additional parameters
            
        Returns:
            Optional[LLMResponse]: Cached response if found and not expired, None otherwise
        """
        key = self._generate_key(messages, **kwargs)
        
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                # Check if expired
                if time.time() < entry["expires_at"]:
                    self.logger.info(f"Cache hit for key: {key[:8]}...")
                    return entry["response"]
                else:
                    # Remove expired entry
                    del self._cache[key]
                    self.logger.info(f"Cache miss (expired) for key: {key[:8]}...")
            else:
                self.logger.info(f"Cache miss (not found) for key: {key[:8]}...")
        
        return None
    
    def set(self, messages: list, response: LLMResponse, ttl: Optional[int] = None, **kwargs):
        """
        Set a response in the cache.
        
        Args:
            messages (list): List of messages
            response (LLMResponse): Response to cache
            ttl (Optional[int]): Time-to-live in seconds. If None, uses default TTL.
            **kwargs: Additional parameters
        """
        key = self._generate_key(messages, **kwargs)
        expires_at = time.time() + (ttl or self.default_ttl)
        
        with self._lock:
            self._cache[key] = {
                "response": response,
                "expires_at": expires_at
            }
        
        self.logger.info(f"Response cached with key: {key[:8]}..., TTL: {ttl or self.default_ttl}s")
    
    def clear(self):
        """
        Clear all cached responses.
        """
        with self._lock:
            self._cache.clear()
        self.logger.info("Cache cleared")
    
    def size(self) -> int:
        """
        Get the number of cached responses.
        
        Returns:
            int: Number of cached responses
        """
        with self._lock:
            # Remove expired entries first
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items() 
                if current_time >= entry["expires_at"]
            ]
            for key in expired_keys:
                del self._cache[key]
            
            return len(self._cache)
    
    def cleanup(self):
        """
        Remove expired entries from the cache.
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items() 
                if current_time >= entry["expires_at"]
            ]
            for key in expired_keys:
                del self._cache[key]
        
        if expired_keys:
            self.logger.info(f"Cache cleanup removed {len(expired_keys)} expired entries")


# Global cache instance
_llm_cache = None


def get_llm_cache() -> LLmCache:
    """
    Get the global LLM cache instance.
    
    Returns:
        LLmCache: Global LLM cache instance
    """
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = LLmCache()
    return _llm_cache


def clear_llm_cache():
    """
    Clear the global LLM cache.
    """
    global _llm_cache
    if _llm_cache is not None:
        _llm_cache.clear()