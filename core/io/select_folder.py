import tkinter as tk
from tkinter import filedialog

def choose_folder(title="Select a folder"):
    root = tk.Tk()
    root.withdraw()          # hide the empty main window
    root.attributes("-topmost", True)  # bring dialog to front (optional)
    folder = filedialog.askdirectory(title=title)
    root.destroy()
    return folder or None

def choose_file(title="Select a file", filetypes=(("All files", "*.*"),)):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # optional: bring dialog to front
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return path or None