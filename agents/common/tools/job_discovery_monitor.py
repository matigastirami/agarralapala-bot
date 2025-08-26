"""
Performance monitoring and error handling for job discovery operations.
"""

import time
import logging
from functools import wraps
from typing import Dict, Any, Callable, List
from dataclasses import dataclass, field
from collections import defaultdict
import traceback

@dataclass
class OperationStats:
    """Statistics for a specific operation"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls
    
    @property
    def average_time(self) -> float:
        if self.successful_calls == 0:
            return 0.0
        return self.total_time / self.successful_calls
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": round(self.success_rate, 3),
            "average_time": round(self.average_time, 3),
            "min_time": round(self.min_time, 3) if self.min_time != float('inf') else 0,
            "max_time": round(self.max_time, 3),
            "recent_errors": self.errors[-5:]  # Last 5 errors
        }

class JobDiscoveryMonitor:
    """Monitor performance and errors for job discovery operations"""
    
    def __init__(self):
        self.stats: Dict[str, OperationStats] = defaultdict(OperationStats)
        self.start_time = time.time()
    
    def record_operation(self, operation_name: str, duration: float, success: bool, error: str = None):
        """Record the result of an operation"""
        stats = self.stats[operation_name]
        
        stats.total_calls += 1
        if success:
            stats.successful_calls += 1
            stats.total_time += duration
            stats.min_time = min(stats.min_time, duration)
            stats.max_time = max(stats.max_time, duration)
        else:
            stats.failed_calls += 1
            if error and len(stats.errors) < 50:  # Keep last 50 errors
                stats.errors.append(f"{time.strftime('%H:%M:%S')}: {error[:200]}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": round(uptime, 1),
            "operations": {name: stats.to_dict() for name, stats in self.stats.items()},
            "summary": {
                "total_operations": sum(stats.total_calls for stats in self.stats.values()),
                "total_successful": sum(stats.successful_calls for stats in self.stats.values()),
                "total_failed": sum(stats.failed_calls for stats in self.stats.values()),
                "overall_success_rate": self._calculate_overall_success_rate()
            }
        }
    
    def _calculate_overall_success_rate(self) -> float:
        total_calls = sum(stats.total_calls for stats in self.stats.values())
        total_successful = sum(stats.successful_calls for stats in self.stats.values())
        
        if total_calls == 0:
            return 0.0
        return round(total_successful / total_calls, 3)
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats.clear()
        self.start_time = time.time()
        logging.info("Job discovery monitor stats reset")
    
    def log_summary(self):
        """Log a summary of current statistics"""
        stats = self.get_stats()
        logging.info("=== Job Discovery Monitor Summary ===")
        logging.info(f"Uptime: {stats['uptime_seconds']}s")
        logging.info(f"Total operations: {stats['summary']['total_operations']}")
        logging.info(f"Success rate: {stats['summary']['overall_success_rate'] * 100:.1f}%")
        
        for op_name, op_stats in stats["operations"].items():
            logging.info(f"{op_name}: {op_stats['successful_calls']}/{op_stats['total_calls']} "
                        f"({op_stats['success_rate'] * 100:.1f}%) avg: {op_stats['average_time']:.2f}s")

# Global monitor instance
job_monitor = JobDiscoveryMonitor()

def monitor_operation(operation_name: str):
    """Decorator to monitor operation performance and errors"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                success = False
                error_msg = str(e)
                
                # Log the error with context
                logging.error(f"Error in {operation_name}: {str(e)}")
                logging.debug(f"Traceback: {traceback.format_exc()}")
                
                # Re-raise the exception
                raise
                
            finally:
                duration = time.time() - start_time
                job_monitor.record_operation(operation_name, duration, success, error_msg)
                
                # Log slow operations
                if duration > 30:  # Operations taking more than 30 seconds
                    logging.warning(f"Slow operation {operation_name}: {duration:.2f}s")
        
        return wrapper
    return decorator

def get_monitor_stats() -> Dict[str, Any]:
    """Get current monitoring statistics"""
    return job_monitor.get_stats()

def reset_monitor_stats():
    """Reset monitoring statistics"""
    job_monitor.reset_stats()

def log_monitor_summary():
    """Log monitoring summary"""
    job_monitor.log_summary()

# Rate limiting utilities
class RateLimiter:
    """Simple rate limiter for external API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_proceed(self) -> bool:
        """Check if we can make another call"""
        now = time.time()
        
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        # Check if we're under the limit
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record that a call was made"""
        self.calls.append(time.time())
    
    def wait_time(self) -> float:
        """Get time to wait before next call is allowed"""
        if self.can_proceed():
            return 0.0
        
        if not self.calls:
            return 0.0
        
        oldest_call = min(self.calls)
        return self.time_window - (time.time() - oldest_call)

# Rate limiters for different services
SERPAPI_RATE_LIMITER = RateLimiter(max_calls=50, time_window=60)  # 50 calls per minute
PLAYWRIGHT_RATE_LIMITER = RateLimiter(max_calls=30, time_window=60)  # 30 browser operations per minute