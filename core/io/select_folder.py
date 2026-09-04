import tkinter as tk
from tkinter import filedialog
from typing import List, Optional, Sequence, Tuple


def choose_folder(title: str = "Select a folder") -> Optional[str]:
    """Open a folder-selection dialog."""
    root = tk.Tk()
    root.withdraw()          # hide the empty main window
    root.attributes("-topmost", True)  # bring dialog to front (optional)
    folder = filedialog.askdirectory(title=title)
    root.destroy()
    return folder or None


def choose_file(
    title: str = "Select a file",
    filetypes: Sequence[Tuple[str, str]] = (("All files", "*.*"),),
) -> Optional[str]:
    """Open a single-file selection dialog."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # optional: bring dialog to front
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return path or None


def choose_files(
    title: str = "Select files",
    filetypes: Sequence[Tuple[str, str]] = (("All files", "*.*"),),
) -> List[str]:
    """Open a multi-file selection dialog and preserve selection order."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
    root.destroy()
    return list(paths)