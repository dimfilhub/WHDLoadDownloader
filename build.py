"""Build a standalone app for the current OS with PyInstaller (run: python build.py).

Needs: pip install pyinstaller
PyInstaller cannot cross-compile, so build on the OS you are targeting. The result is in dist/:
WHDLoadDownloader.app on macOS, a single WHDLoadDownloader executable on Windows and Linux.
Downloaded archives go to a sources/ folder next to the app.
"""
import plistlib
import re
import subprocess
import sys
from pathlib import Path

try:
    import PyInstaller.__main__
except ImportError:
    sys.exit("PyInstaller is not installed. Run: pip install pyinstaller")

NAME = "WHDLoadDownloader"
ROOT = Path(__file__).resolve().parent
sep = ";" if sys.platform == "win32" else ":"
args = [
    str(ROOT / "gui.py"),
    "--name", NAME,
    "--windowed",
    "--noconfirm",
    "--paths", str(ROOT),
    # The Help windows read these README files at run time
    "--add-data", f"{ROOT / 'README.md'}{sep}.",
    "--add-data", f"{ROOT / 'tabs' / 'downloader' / 'README.md'}{sep}tabs/downloader",
]
icon = next(iter(sorted((ROOT / "assets").glob("icon.*"))), None) if (ROOT / "assets").is_dir() else None
if icon:
    args += ["--icon", str(icon)]
if sys.platform != "darwin":   # Windows/Linux: one executable; macOS: an .app bundle
    args.append("--onefile")
PyInstaller.__main__.run(args)

if sys.platform == "darwin":
    # PyInstaller writes version 0.0.0 into Info.plist; use the app's own version instead.
    version = re.search(r'^VERSION = "(.+)"', (ROOT / "gui.py").read_text(), re.M).group(1)
    app = ROOT / "dist" / f"{NAME}.app"
    plist_path = app / "Contents" / "Info.plist"
    plist = plistlib.loads(plist_path.read_bytes())
    plist["CFBundleShortVersionString"] = plist["CFBundleVersion"] = version
    plist_path.write_bytes(plistlib.dumps(plist))
    subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(app)], check=True)
