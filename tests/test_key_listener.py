"""Regression tests for the fork's hotkey-parsing fix.

Upstream savbell/whisper-writer mapped unknown key names to KeyCode.SPACE,
causing phantom hotkey activations (e.g. config like `ctrl+shift+typo` would
fire on every spacebar press). This fork changed the behavior to silently
skip unknown keys instead. These tests guard against that regression.

`parse_key_combination` does not use `self`, so we can exercise it via the
class without instantiating KeyListener (whose __init__ touches
ConfigManager, PynputBackend, etc.).
"""

from key_listener import KeyCode, KeyListener


def _parse(combo: str):
    return KeyListener.parse_key_combination(None, combo)


def test_unknown_key_does_not_default_to_space():
    """The headline fork fix: an unknown key name in the combo should NOT
    silently become KeyCode.SPACE. If this regresses, users with typos in
    their hotkey config will get phantom activations on every spacebar press."""
    keys = _parse("ctrl+shift+totally_not_a_real_key")

    # SPACE must not appear anywhere in the returned set of keys or frozensets.
    flat = set()
    for item in keys:
        if isinstance(item, frozenset):
            flat.update(item)
        else:
            flat.add(item)
    assert KeyCode.SPACE not in flat


def test_known_combination_parses_correctly():
    """Sanity check: the default activation combo should parse into the
    expected three groups (ctrl modifier, shift modifier, SPACE key)."""
    keys = _parse("ctrl+shift+space")

    # The two modifier frozensets and the SPACE keycode should all be present.
    assert KeyCode.SPACE in keys
    # Ctrl and Shift come back as frozensets (either-side matches).
    has_ctrl_group = any(
        isinstance(k, frozenset) and KeyCode.CTRL_LEFT in k for k in keys
    )
    has_shift_group = any(
        isinstance(k, frozenset) and KeyCode.SHIFT_LEFT in k for k in keys
    )
    assert has_ctrl_group and has_shift_group
