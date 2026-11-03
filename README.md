# WHDLoad Downloader

Download WHDLoad `.lha` game archives from the Retroplay WHDLoad Packs on the grandis.nu FTP server, and search
and filter what you have downloaded.

This project is not affiliated with WHDLoad, Retroplay or grandis.nu. It hosts no game files: it only connects to
the public FTP server and downloads from it on your request. Please respect the server and the rights of the
software authors.

## Requirements

- Python 3.10+ with tkinter, no third-party packages.
- Easiest start: double-click `start_macos.command`, `start_windows.bat` or `start_linux.sh`. It creates a `.venv` and opens the GUI. Or run `python gui.py`.

## GUI

The window has two tabs that share one **sources folder** (default `sources/` next to `gui.py`, remembered between
runs): download archives with the Downloader, find them with the Browser.

### WHDLoad Browser

Search and filter the `.lha` archives in the sources folder. Each file name (`Game_v1.2_AGA_De_2MB_Disk2_1234.lha`) is
parsed into title, version, language, platform, memory, media, other tags and ID.

- **Search** matches the title or file name as you type.
- The left panel has check lists for **Language**, **Platform**, **Memory**, **Media** and **Other tags** (tags seen at least twice), each with a count. Ticking several values in one list shows archives matching any of them; different lists combine, so all must match.
- **Latest version only** keeps just the newest version of each game variant.
- **Only entries without ID** shows archives whose name has no ID.
- **Clear filters** resets the search and all filters.
- Click a column heading to sort, click again to reverse. Double-click a row to reveal the file in Finder/Explorer.
- Archives are grouped by the first character of the title (0-9, A-Z); the groups start collapsed (they open automatically while searching or reviewing the selection).
- Click rows to select them (click again to unselect, Shift+click adds the range from the last clicked row; selected rows are shown in bold). Use **Review selection** to list only the selected rows (filters are ignored while it is on).
- **Export CSV...** saves the listed archives, with their paths, to a CSV file. **Refresh** rescans the sources folder (this also happens when you open the tab).

### WHDLoad Downloader

Connects to the FTP server, lists the packs and downloads the archives you pick. See
[tabs/downloader/README.md](tabs/downloader/README.md) for details.

## License

[MIT](LICENSE)
