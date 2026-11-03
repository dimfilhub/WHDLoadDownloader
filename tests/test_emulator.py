import tempfile
import unittest
from pathlib import Path

from common import emulator


class EmulatorTest(unittest.TestCase):
    def test_resolves_app_bundle_folder_and_binary(self):
        with tempfile.TemporaryDirectory() as d:
            binary = Path(d) / "Amiberry.app" / "Contents" / "MacOS" / "Amiberry"
            binary.parent.mkdir(parents=True)
            binary.write_text("x")
            self.assertEqual(emulator.resolve_executable(Path(d) / "Amiberry.app"), binary)
            self.assertEqual(emulator.resolve_executable(d), binary)       # a folder that holds the .app
            self.assertEqual(emulator.resolve_executable(binary), binary)

    def test_missing_path_resolves_to_none(self):
        self.assertIsNone(emulator.resolve_executable(""))
        self.assertIsNone(emulator.resolve_executable("/no/such/amiberry"))

    def test_launch_command_autoloads_the_archive(self):
        self.assertEqual(emulator.launch_command("/x/amiberry", "/g/Game.lha"),
                         ["/x/amiberry", "--autoload", "/g/Game.lha"])

    def test_fullscreen_and_scanlines_options(self):
        self.assertEqual(emulator.launch_command("/x/a", "/g/G.lha", fullscreen=True, scanlines=True),
                         ["/x/a", "--autoload", "/g/G.lha", "-s", "gfx_fullscreen_amiga=fullwindow",
                          "-s", "gfx_linemode=scanlines"])


if __name__ == "__main__":
    unittest.main()
