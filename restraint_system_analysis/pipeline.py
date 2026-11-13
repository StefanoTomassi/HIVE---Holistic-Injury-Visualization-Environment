"""Interactive entry point of the restraint-system analysis.

One window (:mod:`restraint_system_analysis.input_dialog`) asks for:

1. the run folder (``binout*`` + the main ``.key``);
2. the main keyword (auto-detected);
3. the model folders (e.g. VIVA+ and the vehicle/cockpit model), which are
   searched for ``*INCLUDE`` files.

The inputs are remembered between runs in ``~/.hive/restraint_last_paths.json``.

Results are written to ``<run folder>/hive_restraint``.
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from restraint_system_analysis import progress
from restraint_system_analysis.context import AnalysisPlan, SimulationFiles
from restraint_system_analysis.example import example_results
from restraint_system_analysis.hbm import HbmResults, run_hbm_analysis
from restraint_system_analysis.input_dialog import EXAMPLE

LAST_PATHS_FILE = Path.home() / ".hive" / "restraint_last_paths.json"
KEYWORD_SUFFIXES = (".key", ".k", ".dyn")


def load_last_paths() -> dict:
    try:
        return json.loads(LAST_PATHS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_last_paths(files: SimulationFiles) -> None:
    try:
        LAST_PATHS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_PATHS_FILE.write_text(json.dumps({
            "simulation_dir": str(files.simulation_dir),
            "main_keyword": str(files.main_keyword),
            "model_dirs": [str(folder) for folder in files.model_dirs],
        }, indent=2), encoding="utf-8")
    except OSError:
        pass


def find_main_keyword(run_dir: Path) -> List[Path]:
    """Return keyword files in ``run_dir`` that look like a main input deck.

    A main deck terminates the run (``*CONTROL_TERMINATION``); include-only
    files such as contact definitions do not.
    """
    candidates = [p for p in sorted(run_dir.iterdir())
                  if p.is_file() and p.suffix.lower() in KEYWORD_SUFFIXES]
    main_decks = []
    for path in candidates:
        try:
            text = path.read_text(encoding="latin-1", errors="replace").upper()
        except OSError:
            continue
        if "*CONTROL_TERMINATION" in text:
            main_decks.append(path)
    return main_decks or candidates


def select_simulation_files() -> Optional[Union[SimulationFiles, str]]:
    """Show the input window (run folder, main keyword, model folders).

    Returns :data:`~restraint_system_analysis.input_dialog.EXAMPLE` when the
    user asks for the bundled example results instead.
    """
    from restraint_system_analysis.input_dialog import ask_simulation_files

    files = ask_simulation_files(load_last_paths(), find_main_keyword)
    if isinstance(files, SimulationFiles):
        save_last_paths(files)
    return files


def run(files: SimulationFiles, plan: AnalysisPlan = AnalysisPlan()) -> Optional[HbmResults]:
    """Run the analyses enabled in ``plan`` (v1: HBM only)."""
    if not plan.hbm:
        return None
    return run_hbm_analysis(files)


def main() -> Optional[HbmResults]:
    """Select inputs interactively and run the restraint-system analysis."""
    progress.start("Waiting for input selection — fill in the 'restraint analysis "
                   "inputs' window (it may open behind the browser)")
    try:
        files = select_simulation_files()
        if files is None:
            progress.finish("cancelled")
            return None
        if files == EXAMPLE:
            progress.finish()
            return example_results()
        progress.update(0.01, f"Run folder: {files.simulation_dir}")
        results = run(files)
    except Exception as error:
        progress.finish(f"{type(error).__name__}: {error}")
        raise
    progress.finish()
    return results


if __name__ == "__main__":
    result = main()
    if result is not None:
        print(json.dumps(result.to_store(), indent=2))
