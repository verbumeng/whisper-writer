"""Behavioral tests for ConfigManager (src/utils.py).

ConfigManager is a singleton that loads config_schema.yaml, extracts default
values, and merges a user override file on top. These tests exercise the real
class against the real schema so that any mismatch between the two is caught.
"""

import pytest
from utils import ConfigManager


@pytest.fixture(autouse=True)
def _reset_singleton():
    """ConfigManager stores state in a class-level `_instance`. Reset between
    tests so they don't interfere with each other."""
    ConfigManager._instance = None
    yield
    ConfigManager._instance = None


def test_initialize_populates_defaults_from_schema():
    """`initialize()` should load the real schema and expose default values
    via `get_config_value`. If `extract_value` regresses (e.g. starts returning
    the whole leaf dict instead of just the `value` field), the returned
    default won't match the schema's declared default."""
    ConfigManager.initialize()

    # Real defaults from src/config_schema.yaml
    assert ConfigManager.get_config_value("model_options", "use_api") is False
    assert ConfigManager.get_config_value("recording_options", "activation_key") == "ctrl+shift+space"
    assert ConfigManager.get_config_value("recording_options", "sample_rate") == 16000


def test_set_and_get_roundtrip():
    """Setting a value and reading it back should return the same value —
    exercises both set_config_value's nested-key walk and get_config_value's
    lookup path."""
    ConfigManager.initialize()

    ConfigManager.set_config_value("cuda", "model_options", "local", "device")
    assert ConfigManager.get_config_value("model_options", "local", "device") == "cuda"


def test_get_unknown_key_returns_none():
    """Looking up a non-existent key should return None, not raise. Downstream
    code relies on this (e.g., `if ConfigManager.get_config_value(...)`)."""
    ConfigManager.initialize()

    assert ConfigManager.get_config_value("does_not_exist") is None
    assert ConfigManager.get_config_value("model_options", "does_not_exist") is None
