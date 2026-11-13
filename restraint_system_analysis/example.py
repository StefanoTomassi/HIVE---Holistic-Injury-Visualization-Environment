"""Bundled example results, so the GUI can be tried without a simulation."""

from pathlib import Path

from restraint_system_analysis.hbm import (
    CRITERIA_CSV,
    DERIVED_CSV,
    STATUS_JSON,
    HbmResults,
)
from restraint_system_analysis.hbm_criteria import REGIONS

EXAMPLE_DIR = Path(__file__).resolve().parent / "example_results"


def example_results() -> HbmResults:
    """Return the pre-computed Test_Run_16 results shipped with HIVE."""
    if not (EXAMPLE_DIR / STATUS_JSON).is_file():
        raise FileNotFoundError(f"Example results missing in {EXAMPLE_DIR}")
    region_csvs = {}
    for region in REGIONS:
        path = EXAMPLE_DIR / f"restraint_hbm_{region.lower()}.csv"
        if path.is_file():
            region_csvs[region] = str(path)
    return HbmResults(
        output_dir=EXAMPLE_DIR,
        criteria_csv=EXAMPLE_DIR / CRITERIA_CSV,
        derived_csv=EXAMPLE_DIR / DERIVED_CSV,
        region_csvs=region_csvs,
        status_json=EXAMPLE_DIR / STATUS_JSON,
    )
