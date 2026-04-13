"""Put `src/` on sys.path so tests can `from utils import ConfigManager`,
mirroring how the app itself runs (src/ is its working dir)."""

import sys
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
