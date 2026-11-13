"""Build Dynasaur objects, criteria and visualisations for HBM injury metrics.

Each builder checks that the entities it needs exist in the run (via the
:class:`HbmModel`) and otherwise returns a :class:`CriterionStatus` that tells
the user which output is missing. Function names and parameters follow the
VIVA+ reference definitions in ``model/postprocess/Dynasaur``.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence

from core.io.create_objects import create_objects
from restraint_system_analysis.context import CriterionStatus, HbmModel
from restraint_system_analysis.reference_values import (
    BRIC_CRITICAL_OMEGA,
    HEAD_DAMAGE_PARAMETERS,
    HEAD_DAMAGE_RISK,
    NIC_RISK_SIGMOID,
)

# Region names are Dynasaur ``part_of`` values: Dynasaur splits
# ``<part_of>_<name>`` at the first underscore, so they must not contain one.
HEAD, NECK, THORAX, LOWER = "HEAD", "NECK", "THORAX", "LOWER"
#: Landmark coordinates for the occupant-motion animation (not an injury region).
MOTION = "MOTION"
REGIONS = (HEAD, NECK, THORAX, LOWER, MOTION)
#: Side-view animation uses the x (fore-aft) and z (vertical) coordinates.
MOTION_AXES = ("x", "z")


@dataclass(frozen=True)
class Visualization:
    """One Dynasaur time-history request and its definition."""

    name: str
    part_of: str
    region: str
    y_label: str
    definition: dict

    @property
    def command(self) -> dict:
        return {
            "visualization": f"{self.part_of}_{self.name}",
            "x_label": "time [ms]",
            "y_label": self.y_label,
        }


@dataclass
class CriteriaBundle:
    """Everything needed to write the Dynasaur definition files."""

    objects: List[dict] = field(default_factory=list)
    criteria: List[dict] = field(default_factory=list)
    visualizations: List[Visualization] = field(default_factory=list)
    statuses: List[CriterionStatus] = field(default_factory=list)
    roles: Dict[str, str] = field(default_factory=dict)
    rib_groups: List[str] = field(default_factory=list)
    spine_beams: List[str] = field(default_factory=list)

    def add_node(self, model: HbmModel, name: str) -> None:
        if any(obj["name"] == name for obj in self.objects):
            return
        self.objects.extend(create_objects("NODE", {name: model.nodes[name]}))

    def extend(self, other: "CriteriaBundle") -> None:
        for obj in other.objects:
            if not any(existing["name"] == obj["name"] and existing["type"] == obj["type"]
                       for existing in self.objects):
                self.objects.append(obj)
        self.criteria += other.criteria
        self.visualizations += other.visualizations
        self.statuses += other.statuses
        self.roles.update(other.roles)
        self.rib_groups += other.rib_groups
        self.spine_beams += other.spine_beams


# --- Dynasaur JSON helpers ---------------------------------------------------
def node_vector(node: str, *channels: str) -> dict:
    return {"type": "NODE", "ID": node, "array": [f"(0, {c})" for c in channels]}


def time_vector(node: str) -> dict:
    return node_vector(node, "time")


def cfc(node: str, frequency: int, *channels: str) -> dict:
    return {"function": {"name": "cfc", "param": {
        "cfc": frequency,
        "time": time_vector(node),
        "sampled_array": node_vector(node, *channels),
    }}}


def resultant(data_vector: dict) -> dict:
    return {"function": {"name": "res", "param": {"data_vector": data_vector}}}


def criterion(name: str, part_of: str, function: dict) -> dict:
    return {"name": name, "type_of_criteria": "injury", "part_of": part_of,
            "function": function}


def visualization(name: str, region: str, x: dict, y: dict, y_label: str) -> Visualization:
    return Visualization(
        name=name, part_of=region, region=region, y_label=y_label,
        definition={"name": name, "part_of": region, "x": x, "y": y},
    )


def _missing(names: Sequence[str], model: HbmModel) -> List[str]:
    return [name for name in names if name not in model.nodes]


def _role(roles: Mapping[str, str], key: str) -> str:
    return str(roles.get(key, ""))


# --- Head --------------------------------------------------------------------
def build_head(model: HbmModel, roles: Mapping[str, str]) -> CriteriaBundle:
    """HIC15, head DAMAGE (+ AIS risks) and BrIC input histories."""
    bundle = CriteriaBundle()
    accel = _role(roles, "head_accel_global")
    local = _role(roles, "head_cog_local")

    if _missing([accel], model):
        bundle.statuses.append(CriterionStatus(
            "HIC15", HEAD, False, f"history node '{accel}' not found in keywords"))
    else:
        bundle.add_node(model, accel)
        bundle.roles["head_accel_global"] = accel
        a_res = resultant(cfc(accel, 1000, "x_acceleration", "y_acceleration",
                              "z_acceleration"))
        bundle.criteria.append(criterion("HIC15", HEAD, {"name": "max", "param": {
            "data_vector": {"function": {"name": "HIC_15", "param": {
                "time": time_vector(accel), "a_res": a_res}}}}}))
        bundle.visualizations.append(visualization(
            "head_resultant_acceleration_CFC1000", HEAD, time_vector(accel), a_res,
            "acceleration"))
        bundle.statuses.append(CriterionStatus("HIC15", HEAD, True))

    if _missing([local], model):
        for name in ("BrIC", "DAMAGE"):
            bundle.statuses.append(CriterionStatus(
                name, HEAD, False, f"local history node '{local}' not found"))
        return bundle

    bundle.add_node(model, local)
    bundle.roles["head_cog_local"] = local
    damage = {"name": "DAMAGE", "param": dict(
        ra_x=node_vector(local, "rx_acceleration"),
        ra_y=node_vector(local, "ry_acceleration"),
        ra_z=node_vector(local, "rz_acceleration"),
        time=time_vector(local),
        **HEAD_DAMAGE_PARAMETERS,
    )}
    bundle.criteria.append(criterion("BrIC", HEAD, {"name": "BrIC", "param": {
        "r_vel": node_vector(local, "rx_velocity", "ry_velocity", "rz_velocity"),
        "crit_rx_velocity": BRIC_CRITICAL_OMEGA["x"],
        "crit_ry_velocity": BRIC_CRITICAL_OMEGA["y"],
        "crit_rz_velocity": BRIC_CRITICAL_OMEGA["z"],
    }}))
    bundle.criteria.append(criterion("DAMAGE", HEAD, damage))
    for level, params in HEAD_DAMAGE_RISK.items():
        bundle.criteria.append(criterion(f"DAMAGE_risk_{level}", HEAD, {
            "name": "extended_ccdf_weibull",
            "param": dict(x={"function": damage}, **params),
        }))
    for axis in ("x", "y", "z"):
        bundle.visualizations.append(visualization(
            f"head_r{axis}_velocity", HEAD, time_vector(local),
            node_vector(local, f"r{axis}_velocity"), "angular velocity"))
    bundle.statuses.append(CriterionStatus("DAMAGE", HEAD, True))
    bundle.statuses.append(CriterionStatus("BrIC", HEAD, True))
    return bundle


# --- Neck --------------------------------------------------------------------
def _nic_function(head: str, t1: str) -> dict:
    return {"function": {"name": "NIC", "param": {
        "a_head": cfc(head, 180, "x_acceleration"),
        "a_t1": cfc(t1, 60, "x_acceleration"),
        "time_": time_vector(t1),
    }}}


def build_neck(model: HbmModel, roles: Mapping[str, str]) -> CriteriaBundle:
    """NIC (max and VIVA+ risk). Nij/forces need an upper-neck load cell."""
    bundle = CriteriaBundle()
    head, t1 = _role(roles, "head_accel_global"), _role(roles, "t1")
    missing = _missing([head, t1], model)
    if missing:
        bundle.statuses.append(CriterionStatus(
            "NIC", NECK, False, "history nodes not found: " + ", ".join(missing)))
    else:
        for node in (head, t1):
            bundle.add_node(model, node)
        bundle.roles["t1"] = t1
        nic = _nic_function(head, t1)
        bundle.criteria.append(criterion("NIC_max", NECK, {
            "name": "max", "param": {"data_vector": nic}}))
        bundle.criteria.append(criterion("NIC_risk", NECK, {
            "name": "ccdf_sigmoid",
            "param": dict(x={"function": {"name": "max",
                                          "param": {"data_vector": nic}}},
                          **NIC_RISK_SIGMOID),
        }))
        bundle.visualizations.append(visualization(
            "NIC", NECK, time_vector(t1), nic, "NIC"))
        for label, node in (("head", head), ("T1", t1)):
            bundle.visualizations.append(visualization(
                f"{label}_x_acceleration", NECK, time_vector(node),
                node_vector(node, "x_acceleration"), "acceleration"))
        bundle.statuses.append(CriterionStatus("NIC", NECK, True))

    bundle.statuses.append(CriterionStatus(
        "Nij / neck forces", NECK, False,
        "no upper-neck load cell: add *DATABASE_CROSS_SECTION at OC-C1 and "
        "*DATABASE_SECFORC"))
    return bundle


# --- Thorax ------------------------------------------------------------------
def build_thorax(
    model: HbmModel,
    roles: Mapping[str, str],
    rib_group_names: Sequence[str],
) -> CriteriaBundle:
    """Chest-deflection histories and per-rib peak tensile strain."""
    bundle = CriteriaBundle()
    sternum = _role(roles, "sternum_mid")
    spine = _role(roles, "chest_spine_reference")
    missing = _missing([sternum, spine], model)
    if missing:
        bundle.statuses.append(CriterionStatus(
            "Chest deflection", THORAX, False,
            "history nodes not found: " + ", ".join(missing)))
    else:
        bundle.roles.update({"sternum_mid": sternum, "chest_spine_reference": spine})
        for node in (sternum, spine):
            bundle.add_node(model, node)
            for axis in ("x", "y", "z"):
                bundle.visualizations.append(visualization(
                    f"{node}_{axis}_coordinate", THORAX, time_vector(node),
                    node_vector(node, f"{axis}_coordinate"), "coordinate"))
        bundle.statuses.append(CriterionStatus("Chest deflection", THORAX, True))

    available = [name for name in rib_group_names if name in model.part_groups]
    if not available:
        bundle.statuses.append(CriterionStatus(
            "Rib strain / fracture risk", THORAX, False,
            "rib part groups not found (00_vivaplus_IDs.def not in model folders?)"))
        return bundle
    for name in available:
        bundle.objects.append({"type": "OBJECT", "name": name,
                               "id": model.part_groups[name]})
        bundle.criteria.append(criterion(f"{name}_max_strain", THORAX, {
            "name": "stress_strain_part_max", "param": {
                "object_data": {"type": "OBJECT", "ID": name, "strain_stress": "Strain"},
                "selection_tension_compression": "Tension",
                "integration_point": "Max",
                "nr_largest_elements": 1,
            }}))
    bundle.rib_groups = available
    bundle.statuses.append(CriterionStatus("Rib strain / fracture risk", THORAX, True))
    return bundle


# --- Lower body --------------------------------------------------------------
def build_lower_body(
    model: HbmModel,
    roles: Mapping[str, str],
    spine_set: str,
) -> CriteriaBundle:
    """Pelvis acceleration and thoracic-spine beam forces."""
    bundle = CriteriaBundle()
    pelvis = _role(roles, "pelvis")
    if _missing([pelvis], model):
        bundle.statuses.append(CriterionStatus(
            "Pelvis acceleration", LOWER, False, f"history node '{pelvis}' not found"))
    else:
        bundle.add_node(model, pelvis)
        bundle.roles["pelvis"] = pelvis
        bundle.visualizations.append(visualization(
            "pelvis_resultant_acceleration_CFC1000", LOWER, time_vector(pelvis),
            resultant(cfc(pelvis, 1000, "x_acceleration", "y_acceleration",
                          "z_acceleration")),
            "acceleration"))
        bundle.statuses.append(CriterionStatus("Pelvis acceleration", LOWER, True))

    beams = model.beam_sets.get(spine_set, [])
    if not beams:
        bundle.statuses.append(CriterionStatus(
            "Spine beam forces", LOWER, False,
            f"history beam set '{spine_set}' not found"))
    else:
        names = {f"{spine_set}_{index + 1:02d}": beam_id
                 for index, beam_id in enumerate(beams)}
        bundle.objects.extend(create_objects("ELEMENT", names))
        for name in names:
            bundle.visualizations.append(visualization(
                f"{name}_axial", LOWER,
                {"type": "ELEMENT", "ID": name, "array": ["(0, time)"]},
                {"type": "ELEMENT", "ID": name, "array": ["(0, axial)"]},
                "axial force"))
        bundle.spine_beams = list(names)
        bundle.statuses.append(CriterionStatus("Spine beam forces", LOWER, True))

    for name, reason in (
        ("Femur axial force", "no femur load cell: add *DATABASE_CROSS_SECTION at "
                              "mid-femur L/R and *DATABASE_SECFORC"),
        ("Lumbar forces", "no lumbar load cell: add *DATABASE_CROSS_SECTION at L1-L2 "
                          "and *DATABASE_SECFORC"),
    ):
        bundle.statuses.append(CriterionStatus(name, LOWER, False, reason))
    return bundle


#: Object name of the vehicle reference node used to show motion relative to the car.
VEHICLE_REFERENCE = "VEHICLE-reference"


def _history_node_ids(model: HbmModel) -> set:
    """All node IDs (with include offsets) listed in *DATABASE_HISTORY_NODE cards."""
    from restraint_system_analysis.include_resolver import iter_keyword_blocks

    ids = set()
    for include in model.files:
        wanted = (lambda k: k.startswith("*DATABASE_HISTORY_NODE")
                  and "LOCAL" not in k and "SET" not in k)
        try:
            blocks = list(iter_keyword_blocks(include.path, wanted))
        except OSError:
            continue
        for keyword, lines in blocks:
            for line in lines:
                if keyword.endswith("_ID"):
                    fields = [line[:10]]
                else:
                    fields = [line[i:i + 10] for i in range(0, min(len(line), 80), 10)]
                for field_ in fields:
                    if field_.strip().lstrip("-").isdigit() and int(field_) > 0:
                        ids.add(int(field_) + include.offsets.node)
    return ids


def build_motion(model: HbmModel, chains: Mapping[str, Sequence[str]],
                 vehicle_nodes: Sequence[Mapping[str, object]] = ()) -> CriteriaBundle:
    """Landmark coordinates (side view) for the occupant-motion animation.

    If a vehicle-body history node exists, its coordinates are requested too,
    so the GUI can show the motion relative to the car.
    """
    bundle = CriteriaBundle()
    if vehicle_nodes:
        available = _history_node_ids(model)
        for entry in vehicle_nodes:
            node_id = int(entry.get("id", 0))
            if node_id in available:
                bundle.objects.extend(create_objects("NODE", {VEHICLE_REFERENCE: node_id}))
                for axis in MOTION_AXES:
                    bundle.visualizations.append(visualization(
                        f"{VEHICLE_REFERENCE}_{axis}_coordinate", MOTION,
                        time_vector(VEHICLE_REFERENCE),
                        node_vector(VEHICLE_REFERENCE, f"{axis}_coordinate"),
                        "coordinate"))
                break
    seen: List[str] = []
    for nodes in chains.values():
        for node in nodes:
            if node in seen or node not in model.nodes:
                continue
            seen.append(node)
            bundle.add_node(model, node)
            for axis in MOTION_AXES:
                bundle.visualizations.append(visualization(
                    f"{node}_{axis}_coordinate", MOTION, time_vector(node),
                    node_vector(node, f"{axis}_coordinate"), "coordinate"))
    if not seen:
        bundle.statuses.append(CriterionStatus(
            "Occupant motion", MOTION, False, "no landmark history nodes found"))
    return bundle


def rib_group_names(dictionary: Mapping[str, object]) -> List[str]:
    spec = dictionary.get("rib_groups", {})
    if not isinstance(spec, dict):
        return []
    pattern = str(spec.get("pattern", ""))
    return [pattern.format(rib=rib, side=side)
            for rib in spec.get("ribs", []) for side in spec.get("sides", [])]


def build_all(model: HbmModel, dictionary: Mapping[str, object],
              regions: Optional[Sequence[str]] = None) -> CriteriaBundle:
    """Build all requested regions into one bundle."""
    roles = dictionary.get("nodes", {})
    beam_sets = dictionary.get("beam_sets", {})
    regions = regions or REGIONS
    bundle = CriteriaBundle()
    if HEAD in regions:
        bundle.extend(build_head(model, roles))
    if NECK in regions:
        bundle.extend(build_neck(model, roles))
    if THORAX in regions:
        bundle.extend(build_thorax(model, roles, rib_group_names(dictionary)))
    if LOWER in regions:
        bundle.extend(build_lower_body(
            model, roles, str(beam_sets.get("thoracic_spine", ""))))
    if MOTION in regions:
        bundle.extend(build_motion(model, dictionary.get("motion_chains", {}),
                                   dictionary.get("vehicle_reference_nodes", [])))
    return bundle
