"""
retry.py - Retry logic for failed imports.

Provides a utility to retry importing a module when it fails,
with configurable attempts and delay between retries.
"""

import importlib
import time


def import_with_retry(module_name, retries=3, delay=1.0, backoff=2.0):
    """
    Attempt to import a module, retrying on failure.

    Args:
        module_name (str): The fully qualified module name to import.
        retries (int): Number of retry attempts after the initial try (default: 3).
        delay (float): Seconds to wait before the first retry (default: 1.0).
        backoff (float): Multiplier applied to delay after each retry (default: 2.0).

    Returns:
        module: The imported module.

    Raises:
        ImportError: If the module cannot be imported after all attempts.
    """
    last_error = None
    wait = delay

    for attempt in range(1, retries + 2):
        try:
            module = importlib.import_module(module_name)
            return module
        except ImportError as exc:
            last_error = exc
            if attempt <= retries:
                time.sleep(wait)
                wait *= backoff

    raise ImportError(
        f"Failed to import '{module_name}' after {retries + 1} attempt(s): {last_error}"
    ) from last_error
