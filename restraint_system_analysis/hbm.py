"""Human Body Model (HBM) injury analysis for restraint-system simulations.

Workflow (same pattern as ``whiplash_analysis.whiplash``):
keywords -> named entities -> Dynasaur object/criteria definition files ->
``CriteriaController`` / ``DataVisualizationController`` on ``binout*`` ->
CSV files -> derived metrics computed in Python (BrIC, chest deflection,
rib fracture risk, peak forces).
"""

import json
import math
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from core.io.create_criteria import write_criteria_file
from core.io.create_objects import write_object_file
from restraint_system_analysis import progress
from restraint_system_analysis.context import CriterionStatus, HbmModel, SimulationFiles
from restraint_system_analysis.hbm_criteria import (
    HEAD,
    LOWER,
    NECK,
    REGIONS,
    THORAX,
    CriteriaBundle,
    Visualization,
    build_all,
)
from restraint_system_analysis.hbm_model import load_hbm_dictionary, read_hbm_model
from restraint_system_analysis.reference_values import (
    HIC_RISK_LOGNORMAL,
    RIB_RISK_AGES,
    bric,
    fractured_rib_distribution,
    hic_risk,
    rib_fracture_risk,
)

MODULE_NAME = "hbm"
CSV_SEPARATOR = ";"
METADATA_ROWS = 4
G = 9.80665  # m/s^2

CRITERIA_CSV = "restraint_hbm_criteria.csv"
DERIVED_CSV = "restraint_hbm_derived.csv"
STATUS_JSON = "restraint_hbm_status.json"


@dataclass
class HbmResults:
    """Paths and summary of one HBM analysis."""

    output_dir: Path
    criteria_csv: Optional[Path] = None
    derived_csv: Optional[Path] = None
    region_csvs: Dict[str, str] = field(default_factory=dict)
    status_json: Optional[Path] = None
    statuses: List[CriterionStatus] = field(default_factory=list)
    derived: Dict[str, float] = field(default_factory=dict)

    def to_store(self) -> dict:
        """JSON-serialisable summary for a Dash ``dcc.Store``."""
        return {
            "output_dir": str(self.output_dir),
            "criteria_csv": str(self.criteria_csv) if self.criteria_csv else None,
            "derived_csv": str(self.derived_csv) if self.derived_csv else None,
            "region_csvs": self.region_csvs,
            "status_json": str(self.status_json) if self.status_json else None,
        }


# --- Definition files --------------------------------------------------------
def write_definitions(bundle: CriteriaBundle, output_dir: Path) -> Tuple[Path, Path]:
    """Write the object and criteria definition files for Dynasaur."""
    output_dir.mkdir(parents=True, exist_ok=True)
    object_def = output_dir / "object_definition_restraint_hbm.def"
    criteria_def = output_dir / "criteria_definition_restraint_hbm.def"
    write_object_file(dir=object_def, objects=bundle.objects)
    write_criteria_file(
        dir=criteria_def,
        data_visualization=[v.definition for v in bundle.visualizations],
        criteria=bundle.criteria,
    )
    return object_def, criteria_def


def _region_definition(output_dir: Path, region: str,
                       visualizations: Sequence[Visualization]) -> Path:
    path = output_dir / f"criteria_definition_restraint_hbm_{region.lower()}.def"
    write_criteria_file(dir=path,
                        data_visualization=[v.definition for v in visualizations],
                        criteria=[])
    return path


# --- Dynasaur execution ------------------------------------------------------
def run_criteria(bundle: CriteriaBundle, object_def: Path, criteria_def: Path,
                 data_source: str, output_dir: Path) -> Tuple[Path, List[str]]:
    """Evaluate every criterion; failures are collected, not raised."""
    from dynasaur.plugins.criteria_controller import CriteriaController

    progress.update(0.18, "Loading binout* files into Dynasaur "
                          "(large runs can take a minute or two)")
    controller = CriteriaController(
        calculation_procedure_def_file=str(criteria_def),
        object_def_file=str(object_def),
        data_source=data_source,
    )
    failures: List[str] = []
    total = max(len(bundle.criteria), 1)
    for index, item in enumerate(bundle.criteria):
        name = f"{item['part_of']}_{item['name']}"
        progress.update(0.20 + 0.40 * index / total,
                        f"Criterion {index + 1}/{total}: {name}")
        try:
            controller.calculate({"criteria": name})
        except Exception as error:  # Dynasaur raises many error types
            failures.append(f"{name}: {type(error).__name__}: {error}")
    controller.write_CSV(str(output_dir), filename=CRITERIA_CSV)
    return output_dir / CRITERIA_CSV, failures


def run_visualizations(bundle: CriteriaBundle, object_def: Path, data_source: str,
                       output_dir: Path) -> Tuple[Dict[str, str], List[str]]:
    """Write one time-history CSV per body region."""
    from dynasaur.plugins.data_visualization_controller import (
        DataVisualizationController,
    )

    csvs: Dict[str, str] = {}
    failures: List[str] = []
    total = max(len(bundle.visualizations), 1)
    done = 0
    for region in REGIONS:
        items = [v for v in bundle.visualizations if v.region == region]
        if not items:
            continue
        progress.update(0.60 + 0.30 * done / total,
                        f"Time histories: {region.lower()} (loading binout)")
        definition = _region_definition(output_dir, region, items)
        controller = DataVisualizationController(
            calculation_procedure_def_file=str(definition),
            object_def_file=str(object_def),
            data_source=data_source,
        )
        computed = 0
        for item in items:
            done += 1
            progress.update(0.60 + 0.30 * done / total,
                            f"Time history {done}/{total}: "
                            f"{item.command['visualization']}")
            try:
                controller.calculate(item.command)
                computed += 1
            except Exception as error:
                failures.append(f"{item.command['visualization']}: "
                                f"{type(error).__name__}: {error}")
        if computed:
            filename = f"restraint_hbm_{region.lower()}.csv"
            controller.write_CSV(str(output_dir), filename=filename)
            csvs[region] = str(output_dir / filename)
    return csvs, failures


# --- CSV helpers -------------------------------------------------------------
def read_dynasaur_csv(path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return (metadata rows, numeric values) of a Dynasaur CSV."""
    metadata = pd.read_csv(path, sep=CSV_SEPARATOR, header=None,
                           nrows=METADATA_ROWS, dtype=str).fillna("")
    values = pd.read_csv(path, sep=CSV_SEPARATOR, header=None,
                         skiprows=METADATA_ROWS).apply(pd.to_numeric, errors="coerce")
    return metadata, values


def find_signal(metadata: pd.DataFrame, values: pd.DataFrame,
                name: str) -> Optional[Tuple[np.ndarray, np.ndarray, str]]:
    """Find a visualization by name; return (time, value, unit-label)."""
    for column in range(1, metadata.shape[1]):
        header = " ".join(str(metadata.iloc[row, column]) for row in range(METADATA_ROWS))
        if name in header and "time" not in str(metadata.iloc[2, column]).lower():
            return (values.iloc[:, column - 1].to_numpy(dtype=float),
                    values.iloc[:, column].to_numpy(dtype=float),
                    header)
    return None


def read_criteria_values(path: Path) -> Dict[str, float]:
    """Map ``<criterion name>`` to its scalar value from the criteria CSV."""
    if not path.is_file():
        return {}
    metadata, values = read_dynasaur_csv(str(path))
    result: Dict[str, float] = {}
    if values.empty:
        return result
    for column in range(metadata.shape[1]):
        name = str(metadata.iloc[2, column]).strip()
        value = values.iloc[0, column]
        if name and not pd.isna(value):
            result[name] = float(value)
    return result


def _per_second(header: str) -> float:
    """Factor converting an angular velocity/1-per-time column to 1/s."""
    lowered = header.lower()
    if "/ms" in lowered or "millisecond" in lowered:
        return 1000.0
    if "/s" in lowered or "second" in lowered or "hz" in lowered:
        return 1.0
    return 1000.0  # model units: mm-ms-kg


def _to_g(values: np.ndarray, header: str) -> np.ndarray:
    lowered = header.lower()
    if "g_0" in lowered or "[g]" in lowered or "standard_gravity" in lowered:
        return values
    if "m/s" in lowered or "meter / second" in lowered:
        return values / G
    return values * 1000.0 / G  # mm/ms^2 -> m/s^2 -> g


# --- Derived metrics ---------------------------------------------------------
def compute_derived(bundle: CriteriaBundle, region_csvs: Dict[str, str],
                    criteria: Dict[str, float]) -> Dict[str, Tuple[str, str, float]]:
    """Compute metrics not available as Dynasaur functions.

    Returns ``{name: (region, unit, value)}``.
    """
    derived: Dict[str, Tuple[str, str, float]] = {}

    if HEAD in region_csvs:
        meta, vals = read_dynasaur_csv(region_csvs[HEAD])
        omegas = [find_signal(meta, vals, f"head_r{axis}_velocity") for axis in "xyz"]
        if all(omegas):
            factor = _per_second(omegas[0][2])
            # Cross-check of Dynasaur's unit-aware BrIC criterion.
            derived["BrIC_check"] = (HEAD, "-", bric(*(o[1] * factor for o in omegas)))
        accel = find_signal(meta, vals, "head_resultant_acceleration_CFC1000")
        if accel:
            derived["head_peak_resultant_acceleration"] = (
                HEAD, "g", float(np.nanmax(_to_g(accel[1], accel[2]))))

    if THORAX in region_csvs and "sternum_mid" in bundle.roles:
        meta, vals = read_dynasaur_csv(region_csvs[THORAX])
        sternum, spine = bundle.roles["sternum_mid"], bundle.roles["chest_spine_reference"]
        points = {}
        for node in (sternum, spine):
            coords = [find_signal(meta, vals, f"{node}_{axis}_coordinate") for axis in "xyz"]
            if all(coords):
                points[node] = np.vstack([c[1] for c in coords]).T
        if len(points) == 2:
            distance = np.linalg.norm(points[sternum] - points[spine], axis=1)
            deflection = distance[0] - distance
            derived["chest_deflection_max"] = (THORAX, "mm", float(np.nanmax(deflection)))

    for rib in bundle.rib_groups:
        strain = criteria.get(f"{rib}_max_strain")
        if strain is None:
            continue
        for age in RIB_RISK_AGES:
            derived[f"{rib}_fracture_risk_{age}YO"] = (
                THORAX, "-", rib_fracture_risk(strain, age))
    if bundle.rib_groups:
        for age in RIB_RISK_AGES:
            risks = [derived[key][2] for key in derived
                     if key.endswith(f"_fracture_risk_{age}YO")]
            if risks:
                # Probability of >=1 fractured rib, ribs assumed independent.
                derived[f"any_rib_fracture_risk_{age}YO"] = (
                    THORAX, "-", 1.0 - float(np.prod([1.0 - r for r in risks])))
                # Number of fractured ribs -> thorax AIS (AIS 2005).
                distribution = fractured_rib_distribution(risks)
                derived[f"expected_fractured_ribs_{age}YO"] = (
                    THORAX, "-", float(sum(k * p for k, p in enumerate(distribution))))
                for level in (1, 2, 3):
                    derived[f"thorax_risk_AIS{level}+_{age}YO"] = (
                        THORAX, "-", float(sum(distribution[level:])))

    hic = criteria.get("HIC15")
    if hic is not None:
        for level in HIC_RISK_LOGNORMAL:
            derived[f"HIC15_risk_{level}"] = (HEAD, "-", hic_risk(hic, level))

    if LOWER in region_csvs:
        meta, vals = read_dynasaur_csv(region_csvs[LOWER])
        pelvis = find_signal(meta, vals, "pelvis_resultant_acceleration_CFC1000")
        if pelvis:
            derived["pelvis_peak_resultant_acceleration"] = (
                LOWER, "g", float(np.nanmax(_to_g(pelvis[1], pelvis[2]))))
        forces = [find_signal(meta, vals, f"{beam}_axial") for beam in bundle.spine_beams]
        forces = [f[1] for f in forces if f]
        if forces:
            stacked = np.concatenate(forces)
            derived["spine_beam_max_tension"] = (LOWER, "kN", float(np.nanmax(stacked)))
            derived["spine_beam_max_compression"] = (
                LOWER, "kN", float(-np.nanmin(stacked)))
    return {k: v for k, v in derived.items() if not math.isnan(v[2])}


def write_derived_csv(derived: Dict[str, Tuple[str, str, float]], path: Path) -> None:
    """Write derived metrics in the Dynasaur criteria CSV layout."""
    names = list(derived)
    rows = [
        [derived[n][0] for n in names],
        ["derived"] * len(names),
        names,
        [derived[n][1] for n in names],
        [repr(derived[n][2]) for n in names],
    ]
    path.write_text("\n".join(CSV_SEPARATOR.join(row) for row in rows) + "\n",
                    encoding="utf-8")


# --- Entry point -------------------------------------------------------------
def run_hbm_analysis(files: SimulationFiles,
                     regions: Optional[Sequence[str]] = None) -> HbmResults:
    """Run the complete HBM analysis for one simulation."""
    if files.main_keyword is None:
        raise ValueError("A main keyword file is required for the HBM analysis.")
    if not list(files.simulation_dir.glob("binout*")):
        raise FileNotFoundError(f"No binout* files in {files.simulation_dir}")

    progress.update(0.02, "Resolving *INCLUDE files and reading the HBM model")
    dictionary = load_hbm_dictionary()
    model: HbmModel = read_hbm_model(files.main_keyword, files.model_dirs, dictionary)
    if model.missing_includes:
        print("Warning: include files not found: " + ", ".join(model.missing_includes))

    progress.update(0.15, "Writing Dynasaur object and criteria definitions")
    bundle = build_all(model, dictionary, regions)
    output_dir = files.resolved_output_dir
    object_def, criteria_def = write_definitions(bundle, output_dir)

    from core.io.dynasaur_compat import enable_rcforc_resultant_force
    enable_rcforc_resultant_force()

    results = HbmResults(output_dir=output_dir)
    criteria_csv, criteria_failures = run_criteria(
        bundle, object_def, criteria_def, files.data_source, output_dir)
    results.criteria_csv = criteria_csv
    results.region_csvs, viz_failures = run_visualizations(
        bundle, object_def, files.data_source, output_dir)

    progress.update(0.92, "Computing chest deflection, rib risk and peak values")
    criteria_values = read_criteria_values(criteria_csv)
    derived = compute_derived(bundle, results.region_csvs, criteria_values)
    results.derived = {name: value for name, (_r, _u, value) in derived.items()}
    results.derived_csv = output_dir / DERIVED_CSV
    write_derived_csv(derived, results.derived_csv)

    statuses = list(bundle.statuses)
    for failure in criteria_failures + viz_failures:
        name = failure.split(":", 1)[0]
        statuses.append(CriterionStatus(name, "EVALUATION", False, failure))
    results.statuses = statuses
    results.status_json = output_dir / STATUS_JSON
    results.status_json.write_text(json.dumps({
        "main_keyword": str(files.main_keyword),
        "simulation_dir": str(files.simulation_dir),
        "model_dirs": [str(d) for d in files.model_dirs],
        "hbm_offsets": asdict(model.offsets),
        "missing_includes": model.missing_includes,
        "statuses": [asdict(status) for status in statuses],
        "criteria": criteria_values,
        "derived": results.derived,
    }, indent=2), encoding="utf-8")
    return results


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Command-line entry: ``python -m restraint_system_analysis.hbm RUN KEY MODEL...``."""
    import sys

    args = list(argv if argv is not None else sys.argv[1:])
    if len(args) < 2:
        print("usage: python -m restraint_system_analysis.hbm RUN_DIR MAIN_KEY [MODEL_DIR ...]")
        return
    files = SimulationFiles(simulation_dir=Path(args[0]), main_keyword=Path(args[1]),
                            model_dirs=tuple(Path(a) for a in args[2:]))
    try:
        results = run_hbm_analysis(files)
    except Exception:
        traceback.print_exc()
        raise
    print(json.dumps(results.to_store(), indent=2))
    print(json.dumps(results.derived, indent=2))


if __name__ == "__main__":
    main()
