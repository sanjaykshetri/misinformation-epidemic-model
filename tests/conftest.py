"""Configuration and fixtures for pytest."""

import pytest


@pytest.fixture(scope="session")
def small_population_size():
    """Small population for fast test runs."""
    return 100


@pytest.fixture(scope="session")
def medium_population_size():
    """Medium population for test runs."""
    return 500


@pytest.fixture(scope="session")
def short_duration():
    """Short simulation duration for tests."""
    return 10


@pytest.fixture(scope="session")
def medium_duration():
    """Medium simulation duration for tests."""
    return 30
