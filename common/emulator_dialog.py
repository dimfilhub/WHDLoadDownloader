import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import emulator
from .theme import WB_BLUE

WRAP = 520
DOWNLOAD_INFO = ("Amiberry will now download WHDLoad (by Bert Jahn, from whdload.de) and some helper files "
                 "(RTB boot files, JST and optional Amiga libraries from Aminet) into its WHDBoot folder.\n\n"
                 "This needs an internet connection, takes about a minute and only has to be done once "
                 "(repeat it to update). The files are downloaded by Amiberry, not by this app. WHDLoad is "
                 "free for personal use; see whdload.de for its licence.\n\nContinue?")


class EmulatorDialog(tk.Toplevel):
    """Choose the Amiberry app, open its ROMs folder and download WHDLoad. Saves the choice in `settings`."""

    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.title("Emulator (Amiberry)")
        self.configure(background=WB_BLUE)
        self.transient(parent)
        self.resizable(False, False)
        self.path = tk.StringVar(value=settings.get("amiberry") or str(emulator.detect() or ""))
        self.status = tk.StringVar()
        self.fullscreen = tk.BooleanVar(value=bool(settings.get("fullscreen", False)))
        self.scanlines = tk.BooleanVar(value=bool(settings.get("scanlines", False)))

        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Games are run with the Amiberry emulator. The app does not include Amiberry, "
                  "Kickstart ROMs or WHDLoad.", wraplength=WRAP, justify="left").pack(anchor="w", pady=(0, 10))

        emu = self._section(body, "1. Emulator")
        row = ttk.Frame(emu)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.path).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=self.browse).pack(side="left", padx=(8, 0))
        self._note(emu, "Choose the Amiberry app (or its executable). It is found automatically in an emulator/ "
                        "folder next to this app, in /Applications or on your PATH.")

        roms = self._section(body, "2. Kickstart ROMs")
        self._note(roms, "Copy your own Kickstart ROM files into Amiberry's ROMs folder. If Amiberry still uses "
                         "its free AROS ROM afterwards, press F12 in Amiberry to open its settings and rescan the ROMs "
                         "(see Help).")
        ttk.Button(roms, text="Open ROMs folder", command=self.open_roms).pack(anchor="w", pady=(6, 0))

        whd = self._section(body, "3. WHDLoad")
        self._note(whd, "Needed once to run WHDLoad games. Amiberry downloads it from whdload.de.")
        self.dl_btn = ttk.Button(whd, text="Download WHDLoad files", command=self.download)
        self.dl_btn.pack(anchor="w", pady=(6, 0))
        ttk.Label(whd, textvariable=self.status, wraplength=WRAP - 20, justify="left").pack(anchor="w")

        disp = self._section(body, "Display")
        ttk.Checkbutton(disp, text="Run games fullscreen", variable=self.fullscreen).pack(anchor="w")
        ttk.Checkbutton(disp, text="Scanlines (CRT effect)", variable=self.scanlines).pack(anchor="w", pady=(4, 0))

        bottom = ttk.Frame(body)
        bottom.pack(fill="x", pady=(14, 0))
        ttk.Button(bottom, text="Save", command=self.save).pack(side="right")
        ttk.Button(bottom, text="Cancel", command=self.destroy).pack(side="right", padx=8)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.grab_set()

    @staticmethod
    def _section(parent, title):
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.pack(fill="x", pady=5)
        return frame

    @staticmethod
    def _note(parent, text):
        ttk.Label(parent, text=text, wraplength=WRAP - 20, justify="left").pack(anchor="w", pady=(6, 0))

    def _exe(self, quiet=False):
        exe = emulator.resolve_executable(self.path.get().strip())
        if not exe and not quiet:
            messagebox.showwarning("Amiberry not found", "Choose the Amiberry app (or its executable) first.", parent=self)
        return exe

    def browse(self):
        f = filedialog.askopenfilename(parent=self, title="Choose Amiberry (the .app or the executable)")
        if f:
            self.path.set(f)

    def open_roms(self):
        exe = self._exe()
        roms = exe and emulator.paths(exe).get("rom_path")
        if roms:
            roms.mkdir(parents=True, exist_ok=True)
            emulator.open_folder(roms)
        elif exe:
            messagebox.showinfo("ROMs folder", "Amiberry did not report its ROMs folder.", parent=self)

    def download(self):
        exe = self._exe()
        if not exe:
            return
        if not messagebox.askokcancel("Download WHDLoad files", DOWNLOAD_INFO, parent=self):
            return
        self.dl_btn.state(["disabled"])
        self.status.set("Downloading WHDLoad files from whdload.de… (this can take a minute)")

        def work():
            ok, out = emulator.download_whdboot(exe)
            tail = out.splitlines()[-1] if out else ""
            if self.winfo_exists():
                self.after(0, lambda: self._downloaded(ok, tail))

        threading.Thread(target=work, daemon=True).start()

    def _downloaded(self, ok, tail):
        self.dl_btn.state(["!disabled"])
        self.status.set(("Done. " if ok else "Download failed. ") + tail)

    def save(self):
        exe = self._exe()
        if exe:
            self.settings.set("amiberry", str(exe))
            self.settings.set("fullscreen", self.fullscreen.get())
            self.settings.set("scanlines", self.scanlines.get())
            self.destroy()
