"""Where things live: bundled resources (README) and the folder next to the app (downloaded archives)."""
import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)   # True in an app built with build.py (PyInstaller)
# Read-only files shipped with the app. In a built app they are unpacked to a temporary folder.
PROJECT_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))


def _app_dir():
    """The folder the user sees the app in; in a macOS .app bundle, the folder that holds the .app."""
    if not FROZEN:
        return PROJECT_ROOT
    exe = Path(sys.executable).resolve()
    return exe.parents[3] if sys.platform == "darwin" else exe.parent


DEFAULT_SOURCES_DIR = _app_dir() / "sources"   # where downloaded .lha archives go by default
