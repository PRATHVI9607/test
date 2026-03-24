# test

## Retry Logic for Imports

`retry.py` provides `import_with_retry`, a utility that attempts to import a
Python module and automatically retries with exponential back-off when the
import fails.

### Usage

```python
from retry import import_with_retry

# Import a module, retrying up to 3 times with 1-second initial delay
module = import_with_retry("my_module")

# Customise retry behaviour
module = import_with_retry(
    "my_module",
    retries=5,      # number of retries after the first attempt
    delay=0.5,      # seconds before the first retry
    backoff=2.0,    # multiplier applied to the delay after each retry
)
```

### Running the tests

```bash
python -m unittest test_retry -v
```
