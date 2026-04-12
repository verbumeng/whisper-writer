"""Smoke tests for src/config_schema.yaml — the file that defines every
WhisperWriter setting, its default value, type, and description. Broken schema
means a broken first-run experience, so the CI should catch regressions fast."""

from pathlib import Path

import pytest
import yaml

SCHEMA_PATH = Path(__file__).parent.parent / "src" / "config_schema.yaml"


@pytest.fixture(scope="module")
def schema():
    with SCHEMA_PATH.open() as f:
        return yaml.safe_load(f)


def test_schema_file_exists():
    assert SCHEMA_PATH.is_file(), f"Missing config schema at {SCHEMA_PATH}"


def test_schema_parses_as_yaml(schema):
    assert isinstance(schema, dict) and schema, "Schema must be a non-empty mapping"


def test_top_level_sections_present(schema):
    # These are the sections WhisperWriter's ConfigManager expects.
    for section in ("model_options", "recording_options", "post_processing", "misc"):
        assert section in schema, f"config_schema.yaml missing required section: {section}"


def test_entries_have_value_and_type(schema):
    """Every leaf entry should declare at least a `value` and a `type`. Walk
    recursively and flag any leaf that looks like a config entry but is
    missing these keys — catches accidental half-edits."""

    def walk(node, path=""):
        if not isinstance(node, dict):
            return
        # A leaf config entry is a dict that contains a `value` key.
        if "value" in node:
            assert "type" in node, f"{path}: entry has 'value' but no 'type'"
            return
        for k, v in node.items():
            walk(v, f"{path}.{k}" if path else k)

    walk(schema)
