"""Invariants for src/config_schema.yaml that ConfigManager relies on.
If these break, first-run config generation will silently produce a broken
config — so catch it in CI, not at runtime."""

from pathlib import Path

import pytest
import yaml

SCHEMA_PATH = Path(__file__).parent.parent / "src" / "config_schema.yaml"


@pytest.fixture(scope="module")
def schema():
    with SCHEMA_PATH.open() as f:
        return yaml.safe_load(f)


def test_top_level_sections_present(schema):
    """ConfigManager.load_default_config() walks these top-level keys; if one
    gets renamed, every downstream `get_config_value("<section>", ...)` call
    silently returns None instead of the default."""
    for section in ("model_options", "recording_options", "post_processing", "misc"):
        assert section in schema, f"config_schema.yaml missing required section: {section}"


def test_every_leaf_has_value(schema):
    """ConfigManager's `extract_value` treats a dict containing a `value` key
    as a leaf and everything else as a nested section. A leaf missing `value`
    would be silently treated as an empty section — corrupting the config
    rather than erroring. Walk the schema and assert no such half-edit exists.

    Heuristic: any dict that contains a `description` or `type` key is meant
    to be a leaf, so it must also have a `value`."""

    def walk(node, path=""):
        if not isinstance(node, dict):
            return
        looks_like_leaf = "description" in node or "type" in node
        if looks_like_leaf:
            assert "value" in node, f"{path}: leaf entry missing required 'value' key"
            return
        for k, v in node.items():
            walk(v, f"{path}.{k}" if path else k)

    walk(schema)
