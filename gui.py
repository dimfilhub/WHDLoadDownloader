#!/usr/bin/env python3
"""WHDLoad Downloader main window: one window with two tabs, the Downloader and the Browser. Both share one
download folder (the sources folder). Each tab lives in its own folder under tabs/."""
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from common.about_dialog import AboutDialog
from common.help_dialog import HelpDialog
from common.paths import DEFAULT_SOURCES_DIR, PROJECT_ROOT
from common.settings import Settings
from common.theme import apply_app_theme
from tabs.browser.tab import APP_NAME as BROWSER_NAME, BrowserTab
from tabs.downloader.tab import (APP_NAME as DOWNLOADER_NAME, HELP_SECTIONS as DOWNLOADER_HELP_SECTIONS,
                                 README as DOWNLOADER_README, DownloaderTab)

APP_NAME = "WHDLoad Downloader"
VERSION = "1.0.0"
HERE = PROJECT_ROOT
ABOUT_TEXT = ("WHDLoad Downloader downloads WHDLoad .lha game archives and helps you find them. The window has "
              "two tabs:\n\n"
              "WHDLoad Downloader: browse the Retroplay WHDLoad Packs on the grandis.nu FTP server and download "
              "them into the sources folder.\n\n"
              "WHDLoad Browser: search and filter the archives in the sources folder by language, platform, "
              "memory, media and more.\n\n"
              "@Dimfil 2026\n\n"
              "The WHDLoad packs are created by Retroplay (EAB forum) and everyone who builds WHDLoad packs. "
              "All credit goes to Retroplay and to all the people creating WHDLoad packs.")


def show_about(parent):
    AboutDialog(parent, APP_NAME, VERSION, ABOUT_TEXT)


def show_help(parent):
    HelpDialog(parent, APP_NAME, docs=[
        (f"{DOWNLOADER_NAME} tab", DOWNLOADER_README, DOWNLOADER_HELP_SECTIONS),
        (f"{BROWSER_NAME} tab", HERE / "README.md", ("WHDLoad Browser",)),
    ])


def main():
    root = tk.Tk()
    root.title(f"{APP_NAME} v{VERSION}  ©  DimFil 2026")
    root.minsize(640, 580)
    apply_app_theme(root)

    # The sources folder is remembered between runs; a saved folder that no longer exists is dropped.
    settings = Settings()
    saved = settings.get("sources")
    sources = tk.StringVar(root, value=saved if saved and Path(saved).is_dir() else str(DEFAULT_SOURCES_DIR))

    def on_sources_changed(path=None):
        settings.set("sources", sources.get())
        browser.reload()

    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True)
    downloader = DownloaderTab(tabs, sources, on_destination_change=on_sources_changed,
                               on_quit=root.destroy, on_download_done=lambda: browser.reload())
    tabs.add(downloader, text=DOWNLOADER_NAME)
    browser = BrowserTab(tabs, sources, on_quit=downloader.quit_app)
    tabs.add(browser, text=BROWSER_NAME)
    tabs.bind("<<NotebookTabChanged>>", lambda _e: browser.reload() if tabs.select() == str(browser) else None)

    menubar = tk.Menu(root)
    help_menu = tk.Menu(menubar, name="help", tearoff=False)
    help_menu.add_command(label=f"{APP_NAME} Help", command=lambda: show_help(root))
    help_menu.add_command(label=f"About {APP_NAME}…", command=lambda: show_about(root))
    menubar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menubar)
    root.protocol("WM_DELETE_WINDOW", downloader.quit_app)  # confirms if an FTP session is open
    root.mainloop()


if __name__ == "__main__":
    main()
