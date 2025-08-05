"""
Error Metrics Module for Personal Agent

This module contains functionality for collecting and reporting error metrics.
"""

from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading


class ErrorMetricsCollector:
    """Collects and reports error metrics for monitoring and analysis."""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the error metrics collector.
        
        Args:
            max_history (int): Maximum number of error records to keep
        """
        self.max_history = max_history
        self.error_counts = defaultdict(int)
        self.error_details = deque(maxlen=max_history)
        self.error_rates = defaultdict(lambda: deque(maxlen=100))
        self._lock = threading.Lock()
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """
        Record an error occurrence.
        
        Args:
            error_type (str): Type of error (e.g., "AuthenticationError")
            error_message (str): Error message
            context (Dict[str, Any]): Additional context about the error
        """
        with self._lock:
            # Increment error count
            self.error_counts[error_type] += 1
            
            # Record error details
            error_record = {
                "timestamp": datetime.now(),
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            }
            self.error_details.append(error_record)
            
            # Record error rate
            self.error_rates[error_type].append(datetime.now())
    
    def get_error_counts(self) -> Dict[str, int]:
        """
        Get current error counts by type.
        
        Returns:
            Dict[str, int]: Error counts by type
        """
        with self._lock:
            return dict(self.error_counts)
    
    def get_error_rate(self, error_type: str, window_minutes: int = 60) -> float:
        """
        Get error rate for a specific error type within a time window.
        
        Args:
            error_type (str): Type of error
            window_minutes (int): Time window in minutes
            
        Returns:
            float: Error rate (errors per minute)
        """
        with self._lock:
            now = datetime.now()
            window_start = now - timedelta(minutes=window_minutes)
            
            # Count errors in the window
            errors_in_window = sum(
                1 for timestamp in self.error_rates[error_type]
                if timestamp >= window_start
            )
            
            return errors_in_window / window_minutes if window_minutes > 0 else 0
    
    def get_recent_errors(self, limit: int = 10) -> list:
        """
        Get recent error records.
        
        Args:
            limit (int): Maximum number of records to return
            
        Returns:
            list: Recent error records
        """
        with self._lock:
            return list(self.error_details)[-limit:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of error metrics.
        
        Returns:
            Dict[str, Any]: Error metrics summary
        """
        # Get error counts first
        error_counts = self.get_error_counts()
        total_errors = sum(error_counts.values())
        
        # Calculate error rates for each error type
        error_rates_1h = {}
        error_rates_5m = {}
        for error_type in error_counts:
            error_rates_1h[error_type] = self.get_error_rate(error_type, 60)
            error_rates_5m[error_type] = self.get_error_rate(error_type, 5)
        
        summary = {
            "total_errors": total_errors,
            "error_counts": error_counts,
            "error_rates_1h": error_rates_1h,
            "error_rates_5m": error_rates_5m
        }
        return summary
    
    def reset_metrics(self):
        """Reset all error metrics."""
        with self._lock:
            self.error_counts.clear()
            self.error_details.clear()
            for rate_queue in self.error_rates.values():
                rate_queue.clear()


# Global error metrics collector instance
error_metrics_collector = ErrorMetricsCollector()