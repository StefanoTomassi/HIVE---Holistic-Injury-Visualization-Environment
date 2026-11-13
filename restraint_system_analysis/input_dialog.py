"""One window to select every input of the restraint analysis.

It replaces the chain of separate folder dialogs. The window shows
what each input is for, is pre-filled with the last-used paths, and
can check that every ``*INCLUDE`` file of the main keyword is found
before the (long) analysis starts.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, List, Optional, Union

from restraint_system_analysis.context import SimulationFiles
from restraint_system_analysis.include_resolver import resolve_includes

RUN_HELP = ("The folder of ONE LS-DYNA run. It must contain the binout* files "
            "and the main .key file of that run.")
KEY_HELP = ("The input deck that was started in LS-DYNA (it contains "
            "*CONTROL_TERMINATION). It is detected automatically from the run folder.")
MODEL_HELP = ("Folders that contain the model files the main .key includes "
              "(*INCLUDE), for example the VIVA+ folder and the generic car / "
              "cockpit folder. Subfolders are searched, so a parent folder such "
              "as '...\\Model' that contains both is enough. These usually stay "
              "the same between runs.")
WRAP = 560
#: Returned instead of SimulationFiles when the user asks for the bundled example.
EXAMPLE = "example"


class InputDialog:
    """Modal tkinter window returning :class:`SimulationFiles` or ``None``."""

    def __init__(self, last: dict,
                 find_main_keyword: Callable[[Path], List[Path]]) -> None:
        self._find_main_keyword = find_main_keyword
        self.result: Optional[Union[SimulationFiles, str]] = None

        self.root = tk.Tk()
        self.root.title("HIVE – restraint analysis inputs")
        self.root.attributes("-topmost", True)
        self.root.resizable(True, False)
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.run_dir = tk.StringVar(value=last.get("simulation_dir", ""))
        self.main_key = tk.StringVar(value=last.get("main_keyword", ""))
        self.check_text = tk.StringVar(value="Includes not checked yet.")

        row = 0
        row = self._heading(frame, row, "1. Simulation run folder", RUN_HELP)
        ttk.Entry(frame, textvariable=self.run_dir, width=80).grid(row=row, column=0, sticky="ew")
        ttk.Button(frame, text="Browse…", command=self._browse_run).grid(
            row=row, column=1, padx=(6, 0))
        row += 1

        row = self._heading(frame, row, "2. Main keyword file", KEY_HELP)
        self.key_box = ttk.Combobox(frame, textvariable=self.main_key, width=78)
        self.key_box.grid(row=row, column=0, sticky="ew")
        ttk.Button(frame, text="Browse…", command=self._browse_key).grid(
            row=row, column=1, padx=(6, 0))
        row += 1

        row = self._heading(frame, row, "3. Model folders (searched for *INCLUDE files)",
                            MODEL_HELP)
        self.model_list = tk.Listbox(frame, height=4)
        self.model_list.grid(row=row, column=0, sticky="ew")
        for folder in last.get("model_dirs", []):
            if Path(folder).is_dir():
                self.model_list.insert(tk.END, folder)
        buttons = ttk.Frame(frame)
        buttons.grid(row=row, column=1, sticky="n", padx=(6, 0))
        ttk.Button(buttons, text="Add…", command=self._add_model).pack(fill="x")
        ttk.Button(buttons, text="Remove", command=self._remove_model).pack(
            fill="x", pady=(4, 0))
        row += 1

        check = ttk.Frame(frame)
        check.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(check, text="Check includes", command=self.check_includes).pack(
            side="left")
        ttk.Label(check, textvariable=self.check_text, wraplength=WRAP - 120).pack(
            side="left", padx=(8, 0))
        row += 1

        actions = ttk.Frame(frame)
        actions.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        ttk.Button(actions, text="Open example results (no simulation needed)",
                   command=self._example).pack(side="left")
        ttk.Button(actions, text="Cancel", command=self._cancel).pack(side="right")
        ttk.Button(actions, text="Run analysis", command=self._run).pack(
            side="right", padx=(0, 6))

        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
        if self.run_dir.get():
            self._detect_keywords(keep_current=True)

    # --- layout helpers --------------------------------------------------
    @staticmethod
    def _heading(frame: ttk.Frame, row: int, title: str, help_text: str) -> int:
        ttk.Label(frame, text=title, font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(10 if row else 0, 0))
        ttk.Label(frame, text=help_text, foreground="#555", wraplength=WRAP).grid(
            row=row + 1, column=0, columnspan=2, sticky="w", pady=(0, 4))
        return row + 2

    def _model_dirs(self) -> List[Path]:
        return [Path(p) for p in self.model_list.get(0, tk.END)]

    # --- actions ---------------------------------------------------------
    def _browse_run(self) -> None:
        folder = filedialog.askdirectory(parent=self.root, title="Simulation run folder",
                                         initialdir=self.run_dir.get() or None)
        if folder:
            self.run_dir.set(str(Path(folder)))
            self._detect_keywords(keep_current=False)

    def _detect_keywords(self, keep_current: bool) -> None:
        run_dir = Path(self.run_dir.get())
        decks = self._find_main_keyword(run_dir) if run_dir.is_dir() else []
        self.key_box["values"] = [str(p) for p in decks]
        current = self.main_key.get()
        if keep_current and current and Path(current).parent == run_dir:
            return
        self.main_key.set(str(decks[0]) if decks else "")
        self.check_text.set("Includes not checked yet.")

    def _browse_key(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.root, title="Main keyword file",
            initialdir=self.run_dir.get() or None,
            filetypes=(("Keyword files", "*.k *.key *.dyn"), ("All files", "*.*")))
        if path:
            self.main_key.set(str(Path(path)))

    def _add_model(self) -> None:
        folder = filedialog.askdirectory(parent=self.root, title="Add a model folder")
        if folder and str(Path(folder)) not in self.model_list.get(0, tk.END):
            self.model_list.insert(tk.END, str(Path(folder)))
            self.check_text.set("Includes not checked yet.")

    def _remove_model(self) -> None:
        for index in reversed(self.model_list.curselection()):
            self.model_list.delete(index)
        self.check_text.set("Includes not checked yet.")

    def _validation_error(self) -> Optional[str]:
        run_dir = Path(self.run_dir.get())
        if not run_dir.is_dir():
            return "Select the simulation run folder."
        if not list(run_dir.glob("binout*")):
            return f"No binout* files in {run_dir}."
        if not Path(self.main_key.get()).is_file():
            return "Select the main keyword file."
        return None

    def check_includes(self) -> Optional[List[str]]:
        """Resolve the includes; return the missing ones (None if inputs invalid)."""
        error = self._validation_error()
        if error:
            self.check_text.set(error)
            return None
        self.check_text.set("Checking…")
        self.root.update_idletasks()
        resolved, missing = resolve_includes(Path(self.main_key.get()), self._model_dirs())
        if missing:
            self.check_text.set(f"{len(resolved)} include files found, {len(missing)} "
                                f"missing: {', '.join(missing[:3])}"
                                + (" …" if len(missing) > 3 else ""))
        else:
            self.check_text.set(f"✓ All {len(resolved)} include files found.")
        return missing

    def _run(self) -> None:
        error = self._validation_error()
        if error:
            messagebox.showwarning("Missing input", error, parent=self.root)
            return
        missing = self.check_includes()
        if missing and not messagebox.askyesno(
                "Include files not found",
                f"{len(missing)} include file(s) were not found in the model folders:\n\n"
                + "\n".join(missing[:10])
                + "\n\nAdd the folder that contains them, or continue anyway?\n"
                  "(Continue may leave some criteria unavailable.)",
                parent=self.root):
            return
        self.result = SimulationFiles(
            simulation_dir=Path(self.run_dir.get()),
            main_keyword=Path(self.main_key.get()),
            model_dirs=tuple(self._model_dirs()),
        )
        self.root.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.root.destroy()

    def _example(self) -> None:
        self.result = EXAMPLE
        self.root.destroy()

    def show(self) -> Optional[Union[SimulationFiles, str]]:
        self.root.lift()
        self.root.focus_force()
        self.root.mainloop()
        return self.result


def ask_simulation_files(last: dict,
                         find_main_keyword: Callable[[Path], List[Path]]
                         ) -> Optional[Union[SimulationFiles, str]]:
    """Show the input window and return the chosen files (``None`` if cancelled)."""
    return InputDialog(last, find_main_keyword).show()
