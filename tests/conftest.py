"""Configuration and fixtures for pytest."""

import pytest
from _pytest.config import hookimpl


# No longer need the pytest_configure hook for string_converters


@pytest.fixture
def bool_converter():
    """Convert string to bool."""
    return lambda x: x.lower() == 'true'
