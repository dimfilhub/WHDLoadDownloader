"""Whole-app check: the main window builds both tabs, the menu, and the Help/About windows."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WINDOW_SCRIPT = """
import json, sys, tkinter as tk
sys.path.insert(0, sys.argv[1])
import gui
out = {}
def fake_mainloop(root):
    notebook = next(w for w in root.winfo_children() if w.winfo_class() == "TNotebook")
    out["tabs"] = [notebook.tab(i, "text") for i in range(notebook.index("end"))]
    out["title"] = root.title()
    out["menu"] = bool(root.cget("menu"))
    gui.show_help(root)
    gui.show_about(root)
    root.update()

    def texts(widget):
        for child in widget.winfo_children():
            if isinstance(child, tk.Text):
                yield child.get("1.0", "end")
            yield from texts(child)
    out["help_and_about"] = "\\n".join(texts(root))
    root.destroy()
tk.Tk.mainloop = fake_mainloop
gui.main()
print(json.dumps(out))
"""


class MainWindowTest(unittest.TestCase):
    def test_builds_both_tabs_in_order(self):
        """Runs gui.main() in a fresh process (on macOS a throw-away Tk window first crashes the real one)."""
        with tempfile.TemporaryDirectory() as home:
            env = {**os.environ, "HOME": home, "XDG_CONFIG_HOME": home, "APPDATA": home}
            result = subprocess.run([sys.executable, "-c", WINDOW_SCRIPT, str(ROOT)], env=env, cwd=home,
                                    capture_output=True, text=True, timeout=120)
        if "TclError" in result.stderr:
            self.skipTest("no display available")
        self.assertEqual(result.returncode, 0, result.stderr)
        seen = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(seen["tabs"], ["WHDLoad Downloader", "WHDLoad Browser"])
        self.assertTrue(seen["title"].startswith("WHDLoad Downloader v"))
        self.assertTrue(seen["menu"])
        text = seen["help_and_about"]
        for tab, marker in (("Browser", "Export CSV"), ("Downloader", "Downloads mirror the server layout")):
            self.assertIn(marker, text, f"the Help window lost the {tab} text")


if __name__ == "__main__":
    unittest.main()
