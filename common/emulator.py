"""Launch WHDLoad games in the Amiberry emulator. The app only starts Amiberry (`--autoload game.lha`); the
Kickstart ROMs and WHDLoad itself live in Amiberry's own folders and are supplied by the user."""
import shutil
import subprocess
import sys
from pathlib import Path

from .paths import APP_DIR

MAC_BINARY = Path("Contents") / "MacOS" / "Amiberry"


def resolve_executable(path):
    """Return the real Amiberry binary for a path the user picked (an .app bundle, a folder or the binary), or None."""
    if not path:
        return None
    p = Path(path).expanduser()
    if p.is_dir() and p.suffix.lower() == ".app":
        p = p / MAC_BINARY
    elif p.is_dir():
        for name in ("Amiberry.app", "amiberry.exe", "Amiberry.exe", "amiberry", "Amiberry"):
            found = resolve_executable(p / name)
            if found:
                return found
        return None
    return p if p.is_file() else None


def detect():
    """Look for Amiberry in the usual places (an emulator/ folder next to the app, /Applications, PATH)."""
    candidates = [APP_DIR / "emulator", Path("/Applications/Amiberry.app"), Path.home() / "Applications" / "Amiberry.app"]
    for c in candidates:
        found = resolve_executable(c)
        if found:
            return found
    on_path = shutil.which("amiberry")
    return Path(on_path) if on_path else None


def launch_command(exe, archive, fullscreen=False, scanlines=False):
    cmd = [str(exe), "--autoload", str(archive)]
    if fullscreen:
        cmd += ["-s", "gfx_fullscreen_amiga=fullwindow"]   # borderless full-screen window on the desktop
    if scanlines:
        cmd += ["-s", "gfx_linemode=scanlines"]            # CRT-style black lines between display lines
    return cmd


def paths(exe):
    """Amiberry's own folders as {name: Path}, read from `--dump-paths` (empty if that fails)."""
    try:
        out = subprocess.run([str(exe), "--dump-paths"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    found = {}
    for line in out.splitlines():
        key, sep, value = line.partition("=")
        if sep and value:
            found[key.strip()] = Path(value.strip())
    return found


def missing_setup(exe):
    """Human-readable list of what Amiberry still needs before WHDLoad games run (empty if all looks fine)."""
    p = paths(exe)
    problems = []
    whdboot = p.get("whdboot_path")
    if whdboot and not (whdboot / "WHDLoad").exists():
        problems.append("WHDLoad is not installed yet. Use 'Download WHDLoad files' in the Emulator window.")
    return problems


def launch(exe, archive, fullscreen=False, scanlines=False):
    """Start Amiberry on a WHDLoad .lha without waiting for it. Raises OSError if it cannot start."""
    return subprocess.Popen(launch_command(exe, archive, fullscreen, scanlines), stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def download_whdboot(exe):
    """Run Amiberry's own `--download-whdboot` (fetches WHDLoad from whdload.de). Returns (ok, output)."""
    try:
        r = subprocess.run([str(exe), "--download-whdboot"], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def open_folder(path):
    if sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    elif sys.platform.startswith("win"):
        subprocess.run(["explorer", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])
