"""
Retry utilities with exponential backoff for resilient API calls.
"""

import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

def retry_with_backoff(
    max_retries: int = 3,
    backoff_seconds: float = 1,
    exponential_base: float = 2,
    exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """
    Decorator for retrying failed operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_seconds: Initial backoff time in seconds
        exponential_base: Base for exponential backoff (2 = double each time)
        exceptions: Tuple of exceptions to catch and retry on
    
    Example:
        @retry_with_backoff(max_retries=3, backoff_seconds=1)
        def call_member_1_service():
            # This will retry up to 3 times if it fails
            response = requests.get('http://member-1:8001/api/v1/cases')
            return response.json()
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    # Try to execute the function
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise the exception
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "attempts": max_retries,
                                "error": str(e),
                                "args": str(args),
                                "kwargs": str(kwargs)
                            }
                        )
                        raise
                    
                    # Calculate backoff time
                    wait_time = backoff_seconds * (exponential_base ** attempt)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}, "
                        f"retrying in {wait_time:.2f}s",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                            "wait_time": wait_time,
                            "error": str(e)
                        }
                    )
                    
                    # Wait before retrying
                    time.sleep(wait_time)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


# Example usage in scheduler.py:
# from retry_utils import retry_with_backoff
#
# @retry_with_backoff(max_retries=3, backoff_seconds=1)
# def get_all_undertrial_cases(self):
#     url = f"{self.eligibility_service_url}/api/v1/cases/under_trial"
#     response = requests.get(url, timeout=30)
#     response.raise_for_status()
#     return response.json()