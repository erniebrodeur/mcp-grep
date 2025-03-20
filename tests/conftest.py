"""Configuration and fixtures for pytest."""

import pytest
from _pytest.config import hookimpl


@hookimpl(trylast=True)
def pytest_configure(config):
    """Configure pytest with extra type converters for pytest-bdd."""
    # Register a Boolean type converter
    config.addinivalue_line(
        "markers",
        "Boolean: mark a parameter as boolean"
    )

    # Override type conversion for Boolean
    from pytest_bdd import given, when, then
    from pytest_bdd.parser import string_converters
    string_converters['Boolean'] = lambda x: x.lower() == 'true'


@pytest.fixture
def bool_converter():
    """Convert string to bool."""
    return lambda x: x.lower() == 'true'
