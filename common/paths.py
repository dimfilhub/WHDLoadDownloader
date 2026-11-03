"""Where things live in the project: the folder that holds gui.py."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES_DIR = PROJECT_ROOT / "sources"   # where downloaded .lha archives go by default
