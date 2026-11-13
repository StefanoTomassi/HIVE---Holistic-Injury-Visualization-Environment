"""Unit tests for the restraint-system HBM pipeline (no binout required)."""

import json
import math
from pathlib import Path

import pytest

from restraint_system_analysis.context import IdOffsets
from restraint_system_analysis.hbm import write_derived_csv
from restraint_system_analysis.hbm_criteria import (
    HEAD,
    LOWER,
    NECK,
    THORAX,
    build_all,
)
from restraint_system_analysis.hbm_model import (
    parse_local_history_nodes,
    read_hbm_model,
)
from restraint_system_analysis.include_resolver import (
    parse_transform_offsets,
    resolve_includes,
)
from restraint_system_analysis.reference_values import bric, rib_fracture_risk

HBM_NODES = """*KEYWORD
*DATABASE_HISTORY_NODE_ID
$       ID|                              HEADING                                |
   1090010HE-Head-CoG-Accelerometer-Global
*DATABASE_HISTORY_NODE_LOCAL_ID
   1090000   1090000         1         0
HE-Head-COG-Local
*DATABASE_HISTORY_NODE_ID
   4091010TX-T1_COG
*DATABASE_HISTORY_NODE_ID
   4093503TX-Sternum_Mid
*DATABASE_HISTORY_NODE_ID
   4091080TX-T8_COG
*DATABASE_HISTORY_BEAM_SET
    404001
*SET_BEAM_TITLE
TX-Spine_force_output
    404001
   2143076   2143077
*PART
TX-Ribcage-R4-Cortical-L
    403044    403044    403004
*END
"""

HBM_MAIN = """*KEYWORD
*INCLUDE_PATH
../hbm/common/
*INCLUDE
nodes_and_outputs.k
*END
"""

RUN_MAIN = """*KEYWORD
*INCLUDE_PATH
../cluster_only/vivaplus/
*INCLUDE_TRANSFORM
vivaplus-test.key
  10000000  10000000  10000000  10000000  10000000  10000000  10000000
  10000000
                                                 0
         1
*CONTROL_TERMINATION
     150.0
*END
"""

IDS_DEF = {
    "OBJECTS": [
        {"type": "OBJECT", "name": "TX-Ribcage-R4-Cortical-L", "id": [403044]},
        {"type": "OBJECT", "name": "TX-Ribcage-R4-Cortical-R", "id": [453044]},
    ]
}


@pytest.fixture()
def model_tree(tmp_path: Path):
    """Run folder whose include paths only resolve via the model folder."""
    run = tmp_path / "run"
    hbm = tmp_path / "models" / "hbm"
    (hbm / "main").mkdir(parents=True)
    (hbm / "common").mkdir(parents=True)
    (hbm / "post").mkdir(parents=True)
    run.mkdir()
    (run / "main.key").write_text(RUN_MAIN)
    (hbm / "main" / "vivaplus-test.key").write_text(HBM_MAIN)
    (hbm / "common" / "nodes_and_outputs.k").write_text(HBM_NODES)
    (hbm / "post" / "00_vivaplus_IDs.def").write_text(json.dumps(IDS_DEF))
    return run / "main.key", tmp_path / "models"


def test_transform_offsets_parsed() -> None:
    offsets = parse_transform_offsets("  10000000       100         0         0         5")
    assert offsets == IdOffsets(node=10000000, element=100, part=0, material=0, set=5)


def test_resolver_finds_files_and_accumulates_offsets(model_tree) -> None:
    main_key, models = model_tree
    files, missing = resolve_includes(main_key, [models])
    assert missing == []
    names = [f.path.name for f in files]
    assert names == ["main.key", "vivaplus-test.key", "nodes_and_outputs.k"]
    assert files[2].offsets.node == 10000000 and files[2].depth == 2


def test_resolver_reports_missing(tmp_path: Path) -> None:
    main = tmp_path / "main.key"
    main.write_text("*KEYWORD\n*INCLUDE\nnot_there.k\n*END\n")
    _files, missing = resolve_includes(main, [])
    assert missing == ["not_there.k"]


def test_local_history_node_heading_on_next_card() -> None:
    nodes = parse_local_history_nodes(["   1090000   1090000         1         0",
                                       "HE-Head-COG-Local"])
    assert nodes == {"HE-Head-COG-Local": 1090000}


def test_model_ids_are_offset(model_tree) -> None:
    main_key, models = model_tree
    model = read_hbm_model(main_key, [models])
    assert model.nodes["HE-Head-CoG-Accelerometer-Global"] == 11090010
    assert model.nodes["HE-Head-COG-Local"] == 11090000
    assert model.beam_sets["TX-Spine_force_output"] == [12143076, 12143077]
    assert model.part_groups == {"TX-Ribcage-R4-Cortical-L": [10403044]}


def test_build_all_statuses_and_json(model_tree) -> None:
    main_key, models = model_tree
    bundle = build_all(read_hbm_model(main_key, [models]),
                       json.loads((Path(__file__).parents[1]
                                   / "vivaplus_hbm_dictionary.json").read_text()))
    available = {(s.region, s.name): s.available for s in bundle.statuses}
    assert available[(HEAD, "HIC15")]
    assert available[(NECK, "NIC")]
    assert not available[(NECK, "Nij / neck forces")]
    assert not available[(LOWER, "Pelvis acceleration")]  # node absent in fixture
    assert available[(THORAX, "Rib strain / fracture risk")]
    names = {c["name"] for c in bundle.criteria}
    assert {"HIC15", "BrIC", "NIC_max", "TX-Ribcage-R4-Cortical-L_max_strain"} <= names
    node_ids = {o["name"]: o["id"] for o in bundle.objects if o["type"] == "NODE"}
    assert node_ids["TX-T1_COG"] == [14091010]
    json.dumps([c for c in bundle.criteria])  # serialisable


def test_bric_and_rib_risk() -> None:
    assert bric([66.25], [0.0], [0.0]) == pytest.approx(1.0)
    assert bric([0.0], [56.45], [42.87]) == pytest.approx(math.sqrt(2))
    assert rib_fracture_risk(0.0, 50) == 0.0
    young, old = rib_fracture_risk(0.03, 25), rib_fracture_risk(0.03, 75)
    assert 0.0 < young < old < 1.0


def test_derived_csv_layout(tmp_path: Path) -> None:
    path = tmp_path / "derived.csv"
    write_derived_csv({"BrIC_check": (HEAD, "-", 0.5)}, path)
    rows = path.read_text().splitlines()
    assert rows == ["HEAD", "derived", "BrIC_check", "-", "0.5"]


def test_hic_risk_curve() -> None:
    from restraint_system_analysis.reference_values import hic_risk
    # NHTSA log-normal curve: 50 % AIS3+ at HIC = exp(mu).
    assert hic_risk(math.exp(7.45231), "AIS3+") == pytest.approx(0.5)
    assert hic_risk(700, "AIS3+") == pytest.approx(0.1116, abs=1e-3)
    assert hic_risk(700, "AIS2+") > hic_risk(700, "AIS3+")
    assert hic_risk(0, "AIS3+") == 0.0


def test_fractured_rib_distribution() -> None:
    from restraint_system_analysis.reference_values import fractured_rib_distribution
    distribution = fractured_rib_distribution([0.5, 0.5, 0.2])
    assert sum(distribution) == pytest.approx(1.0)
    assert len(distribution) == 4
    assert distribution[0] == pytest.approx(0.5 * 0.5 * 0.8)
    assert distribution[3] == pytest.approx(0.5 * 0.5 * 0.2)


def test_bundled_example_results_are_complete() -> None:
    from restraint_system_analysis.example import example_results
    from restraint_system_analysis.hbm_criteria import REGIONS
    results = example_results()
    store = results.to_store()
    assert set(store["region_csvs"]) == set(REGIONS)
    status = json.loads(Path(store["status_json"]).read_text(encoding="utf-8"))
    assert status["example"] is True
    assert "HIC15" in status["criteria"]
    assert "thorax_risk_AIS3+_50YO" in status["derived"]
    assert "MSc" not in Path(store["status_json"]).read_text(encoding="utf-8")


def test_input_dialog_example_choice() -> None:
    pytest.importorskip("tkinter")
    from restraint_system_analysis.input_dialog import EXAMPLE, InputDialog
    try:
        dialog = InputDialog({}, lambda _path: [])
    except Exception as error:  # no display available
        pytest.skip(f"tkinter unavailable: {error}")
    dialog.root.after(100, dialog._example)
    assert dialog.show() == EXAMPLE
