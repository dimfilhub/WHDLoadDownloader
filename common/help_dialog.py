import re
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import ttk

from .theme import LINK_COLOR, TEXT_COLOR, WB_BLUE

FALLBACK = "The README.md file could not be found."


def readme_sections(text, titles):
    """Return [(title, body)] for the `## title` sections of the README that are in `titles`."""
    parts = re.split(r"^#{2,3} (.+)$", text, flags=re.M)
    found = {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    return [(t, found[t]) for t in titles if t in found]


class HelpDialog(tk.Toplevel):
    """Shows selected sections of the README in a scrollable window."""

    def __init__(self, parent, name, docs):
        """docs: [(heading or None, readme path, section titles)]."""
        super().__init__(parent)
        self.docs = docs
        self.title(f"{name} Help")
        self.configure(background=WB_BLUE)
        self.transient(parent)
        self.geometry("720x560")

        frame = ttk.Frame(self, padding=8)
        frame.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")
        self.text = tk.Text(frame, wrap="word", padx=10, pady=8, yscrollcommand=scroll.set,
                            borderwidth=0, highlightthickness=0, background=WB_BLUE,
                            foreground=TEXT_COLOR)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.text.yview)
        self.text.tag_configure("h", font=("Helvetica", 14, "bold"), spacing1=10, spacing3=4)
        self.text.tag_configure("top", font=("Helvetica", 18, "bold"), spacing1=14, spacing3=6, underline=True)
        self.text.tag_configure("b", font=("Helvetica", 12, "bold"))
        self.text.tag_configure("code", font=("Courier", 11))
        self._fill()
        self.text.config(state="disabled")
        self.bind("<Escape>", lambda _e: self.destroy())

    def _fill(self):
        for heading, path, titles in self.docs:
            if heading:
                self.text.insert("end", heading + "\n", "top")
            self._fill_doc(path, titles)

    def _fill_doc(self, path, titles):
        try:
            readme = path.read_text(encoding="utf-8")
        except OSError:
            self.text.insert("end", FALLBACK + "\n")
            return
        sections = readme_sections(readme, titles)
        if not sections:
            self.text.insert("end", FALLBACK + "\n")
        for title, body in sections:
            self.text.insert("end", title + "\n", "h")
            in_code = False
            for line in body.splitlines():
                if line.startswith("```"):
                    in_code = not in_code
                elif in_code:
                    self.text.insert("end", "  " + line + "\n", "code")
                else:
                    self._line(line)
            self.text.insert("end", "\n")

    def _plain(self, chunk):
        """Insert text, turning bare URLs into clickable links."""
        for part in re.split(r"(https?://[^\s)]+)", chunk):
            if part.startswith("http"):
                tag = f"link{part}"
                self.text.tag_configure(tag, foreground=LINK_COLOR, underline=True)
                self.text.tag_bind(tag, "<Button-1>", lambda _e, u=part: webbrowser.open(u))
                self.text.tag_bind(tag, "<Enter>", lambda _e: self.text.config(cursor="hand2"))
                self.text.tag_bind(tag, "<Leave>", lambda _e: self.text.config(cursor=""))
                self.text.insert("end", part, tag)
            else:
                self.text.insert("end", part)

    def _line(self, line):
        line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"<(https?://[^>]+)>", r"\1", line)
        line = re.sub(r"^(\d+)\. ", r"  \1. ", line)
        if line.startswith("- "):
            line = "  • " + line[2:]
        # **bold** and `code` spans
        for chunk in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", line):
            if chunk.startswith("**") and chunk.endswith("**") and len(chunk) > 4:
                self.text.insert("end", chunk[2:-2], "b")
            elif chunk.startswith("`") and chunk.endswith("`") and len(chunk) > 2:
                self.text.insert("end", chunk[1:-1], "code")
            else:
                self._plain(chunk)
        self.text.insert("end", "\n")
