"""Compile-check every source file. Catches syntax errors without needing
to install the heavy runtime deps (torch, faster-whisper, PyQt5, etc.)."""

import py_compile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SOURCE_FILES = sorted(
    [ROOT / "run.py"]
    + list((ROOT / "src").glob("*.py"))
    + list((ROOT / "src" / "ui").glob("*.py"))
)


@pytest.mark.parametrize("path", SOURCE_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_source_file_compiles(path):
    py_compile.compile(str(path), doraise=True)
