"""
test_retry.py - Tests for retry import logic.
"""

import sys
import unittest
from unittest.mock import patch, call

from retry import import_with_retry


class TestImportWithRetry(unittest.TestCase):

    def test_successful_import_on_first_try(self):
        """A module that exists should be returned immediately."""
        module = import_with_retry("os")
        import os as expected
        self.assertIs(module, expected)

    def test_no_retries_when_import_succeeds(self):
        """importlib.import_module should only be called once on success."""
        with patch("retry.importlib.import_module", return_value=object()) as mock_import:
            import_with_retry("fake_module", retries=3, delay=0)
            mock_import.assert_called_once_with("fake_module")

    def test_raises_after_all_retries_exhausted(self):
        """ImportError should be raised once all attempts are exhausted."""
        with patch("retry.time.sleep"):
            with patch("retry.importlib.import_module", side_effect=ImportError("not found")):
                with self.assertRaises(ImportError) as ctx:
                    import_with_retry("nonexistent_module", retries=2, delay=0)
        self.assertIn("nonexistent_module", str(ctx.exception))
        self.assertIn("3 attempt(s)", str(ctx.exception))

    def test_retry_count(self):
        """import_module should be called retries+1 times on persistent failure."""
        retries = 3
        with patch("retry.time.sleep"):
            with patch("retry.importlib.import_module", side_effect=ImportError("err")) as mock_import:
                with self.assertRaises(ImportError):
                    import_with_retry("bad_module", retries=retries, delay=0)
        self.assertEqual(mock_import.call_count, retries + 1)

    def test_sleep_called_with_backoff(self):
        """time.sleep should be called with increasing delays."""
        delay = 1.0
        backoff = 2.0
        retries = 3
        with patch("retry.time.sleep") as mock_sleep:
            with patch("retry.importlib.import_module", side_effect=ImportError("err")):
                with self.assertRaises(ImportError):
                    import_with_retry(
                        "bad_module", retries=retries, delay=delay, backoff=backoff
                    )
        expected_calls = [
            call(1.0),
            call(2.0),
            call(4.0),
        ]
        mock_sleep.assert_has_calls(expected_calls)
        self.assertEqual(mock_sleep.call_count, retries)

    def test_succeeds_on_second_attempt(self):
        """Should succeed if import fails once then succeeds."""
        fake_module = object()
        side_effects = [ImportError("transient"), fake_module]
        with patch("retry.time.sleep"):
            with patch("retry.importlib.import_module", side_effect=side_effects) as mock_import:
                result = import_with_retry("flaky_module", retries=2, delay=0)
        self.assertIs(result, fake_module)
        self.assertEqual(mock_import.call_count, 2)


if __name__ == "__main__":
    unittest.main()
