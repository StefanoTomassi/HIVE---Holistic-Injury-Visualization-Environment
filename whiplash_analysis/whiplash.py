"""Whiplash model input discovery."""

import json
import re
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union

from dynasaur.plugins.criteria_controller import CriteriaController
from dynasaur.plugins.data_visualization_controller import DataVisualizationController

from core.dataclasses.simulation_dataclasses import (
    CriteriaDefinition,
    CriteriaFunction,
    CriteriaParamObjectData,
    DataVector,
    DataVisualizationDefinition,
    MaxParameters,
    PercentileParameters,
)
from core.io.create_criteria import create_data_visualization, write_criteria_file
from core.io.create_objects import create_objects, write_object_file
from core.io.dynasaur_compat import enable_rcforc_resultant_force
from core.io.keyword_reader import (
    get_dyna_history_node_id,
    get_dyna_history_beam_id,
    get_dyna_contact,
    get_dyna_beam_section_areas,
    get_dyna_part_sections,
    get_dyna_parts,
    get_elements,
    read_keywords,
)
from core.io.select_folder import choose_files, choose_folder
from whiplash_analysis.reference_values import sigma_max_muscle
from global_energy.get_part_commands import get_part_commands


VIVAPLUS_DICTIONARY_PATH = Path(__file__).with_name("VIVAplus_dictionary.txt")
LIGAMENT_CATEGORY = "ligaments"
FACET_JOINT_CATEGORY = "facet joints"
INTERVERTEBRAL_DISC_CATEGORY = "intervertebral discs"


def read_vivaplus_categories(
    dictionary_path: Union[Path, str] = VIVAPLUS_DICTIONARY_PATH,
) -> Dict[str, Dict[str, Union[int, dict, list]]]:
    """Read the VIVAplus category-to-part mapping."""
    path = Path(dictionary_path)
    if not path.is_file():
        raise FileNotFoundError(f"VIVAplus dictionary not found: {path}")
    with path.open(encoding="utf-8") as dictionary_file:
        categories = json.load(dictionary_file)
    if not isinstance(categories, dict):
        raise ValueError("VIVAplus dictionary must contain a JSON object.")
    normalized = {}
    for category, part_mapping in categories.items():
        normalized[category] = {}
        for part_name, part_data in part_mapping.items():
            if isinstance(part_data, dict):
                normalized[category][str(part_name)] = {
                    key: value for key, value in part_data.items()
                }
            elif isinstance(part_data, list):
                normalized[category][str(part_name)] = list(part_data)
            else:
                normalized[category][str(part_name)] = int(part_data)
    return normalized


def select_vivaplus_parts(
    parts: Mapping[str, int],
    categories: Mapping[str, Mapping[str, Union[int, dict, list]]],
    category_names: Sequence[str],
) -> Dict[str, int]:
    """Select parsed keyword parts listed in the requested VIVAplus categories."""
    category_part_names = set()
    for category_name in category_names:
        for part_name, part_data in categories.get(category_name, {}).items():
            if isinstance(part_data, dict):
                if not isinstance(part_data.get("part_id"), int):
                    raise ValueError(
                        f"VIVAplus entry {part_name!r} must contain an integer part_id"
                    )
            elif not isinstance(part_data, int):
                continue
            category_part_names.add(part_name)
    return {
        part_name: part_id
        for part_name, part_id in parts.items()
        if part_name in category_part_names
    }


def read_model_parts(
    keyword_files: Union[Path, Sequence[Path]],
) -> Dict[str, int]:
    """Read part names and IDs from one or more LS-DYNA keyword files.

    Args:
        keyword_files: One keyword-file path or an ordered sequence of paths.

    Returns:
        A mapping from part names to their integer LS-DYNA IDs.
    """
    files = [keyword_files] if isinstance(keyword_files, Path) else keyword_files
    parts: Dict[str, int] = {}
    for keyword_file in files:
        cards = read_keywords(str(keyword_file))
        parts.update(get_dyna_parts(cards))
    return parts


def create_model_part_objects(parts: Dict[str, int]) -> List[dict]:
    """Create Dynasaur object definitions for model parts.

    Args:
        parts: Mapping from part names to LS-DYNA part IDs.

    Returns:
        Dynasaur-compatible object definition dictionaries.
    """
    return create_objects(type_obj="OBJECT", data=parts)


def create_part_energy_objects(
    parts: Mapping[str, int],
    energy_groups: Mapping[str, Mapping[str, Union[int, dict, list]]],
) -> Tuple[List[dict], List[DataVisualizationDefinition], List[dict]]:
    """Create ENERGY_PART objects and grouped internal-energy visualizations."""
    objects = create_objects(type_obj="ENERGY_PART", data=parts)
    visualizations: List[DataVisualizationDefinition] = []
    definitions: List[dict] = []
    component_to_group = {
        component: group
        for groups in energy_groups.values()
        for group, body_data in groups.items()
        if isinstance(body_data, dict)
        for component in body_data.get("parts", [])
    }
    for part_name in parts:
        if part_name in component_to_group:
            continue
        part_visualizations, part_definitions = get_part_commands(part_name)
        internal_energy = next(
            visualization
            for visualization in part_visualizations
            if visualization.y == "internal_energy"
        )
        visualizations.append(internal_energy)
        definitions.extend(
            definition
            for definition, visualization in zip(
                part_definitions,
                part_visualizations,
            )
            if visualization.y == "internal_energy"
        )
    for groups in energy_groups.values():
        for group, body_data in groups.items():
            if not isinstance(body_data, dict):
                continue
            component_names = [
                component
                for component in body_data.get("parts", [])
                if component in parts
            ]
            if len(component_names) != len(body_data.get("parts", [])):
                continue
            data_vectors = [
                {
                    "type": "ENERGY_PART",
                    "ID": component,
                    "array": ["(0, internal_energy)"],
                }
                for component in component_names
            ]
            summed_vector = data_vectors[0]
            for data_vector in data_vectors[1:]:
                summed_vector = {
                    "function": {
                        "name": "add",
                        "param": {
                            "data_vector_1": summed_vector,
                            "data_vector_2": data_vector,
                        },
                    }
                }
            name = f"{group} Internal Energy"
            part_of = f"Part Energy{group}"
            visualizations.append(
                DataVisualizationDefinition(
                    name=name,
                    part_of=part_of,
                    type="ENERGY_PART",
                    ID=component_names[0],
                    y=group,
                    x="time",
                )
            )
            definitions.append(
                {
                    "name": name,
                    "part_of": part_of,
                    "x": {
                        "type": "ENERGY_PART",
                        "ID": component_names[0],
                        "array": ["(0, time)"],
                    },
                    "y": summed_vector,
                }
            )
    return objects, visualizations, definitions


def create_model_node_objects(cards: Mapping[str, Sequence[str]]) -> List[dict]:
    """Create Dynasaur node objects from history-node keyword cards.

    Only ``*DATABASE_HISTORY_NODE_ID`` cards are processed. The returned
    definitions can be appended to the same object container as part objects.

    Args:
        cards: Keyword cards returned by :func:`read_keywords`.

    Returns:
        Dynasaur-compatible node object definition dictionaries.
    """
    nodes: Dict[str, int] = {}
    for keyword, lines in cards.items():
        if keyword.startswith("*DATABASE_HISTORY_NODE_ID"):
            nodes.update(get_dyna_history_node_id(list(lines)))
    return create_objects(type_obj="NODE", data=nodes)


def create_beam_axial_data_visualization(
    beams: Mapping[str, int],
) -> Tuple[List[dict], List[DataVisualizationDefinition], List[dict]]:
    """Create ELEMENT objects and axial/time visualizations for beam histories."""
    objects = create_objects(type_obj="ELEMENT", data=beams)
    visualizations = [
        DataVisualizationDefinition(
            name=f"{beam_name}_axial",
            part_of=beam_name,
            type="ELEMENT",
            ID=beam_name,
            y="axial",
            x="time",
        )
        for beam_name in beams
    ]
    definitions: List[dict] = []
    for visualization in visualizations:
        create_data_visualization(
            items=definitions,
            name=visualization.name,
            part_of=visualization.part_of,
            ID=visualization.ID,
            crit_type=visualization.type,
            x_crit=visualization.x,
            y_crit=visualization.y,
        )
    return objects, visualizations, definitions


def create_contact_force_data_visualization(
    contacts: Mapping[str, int],
) -> Tuple[
    List[dict],
    List[DataVisualizationDefinition],
    List[dict],
    List[CriteriaDefinition],
]:
    """Create CONTACT resultant-force histories and maximum-force criteria."""
    objects = [
        {
            "type": "CONTACT",
            "name": contact_name,
            "id": [f"{contact_id}m"],
        }
        for contact_name, contact_id in contacts.items()
    ]
    visualizations = [
        DataVisualizationDefinition(
            name=f"{contact_name}_resultant_force",
            part_of=contact_name,
            type="CONTACT",
            ID=contact_name,
            y="resultant_force",
            x="time",
        )
        for contact_name in contacts
    ]
    definitions: List[dict] = []
    criteria: List[CriteriaDefinition] = []
    for visualization in visualizations:
        create_data_visualization(
            items=definitions,
            name=visualization.name,
            part_of=visualization.part_of,
            ID=visualization.ID,
            crit_type=visualization.type,
            x_crit=visualization.x,
            y_crit=visualization.y,
        )
        criteria.append(
            CriteriaDefinition(
                name=f"{visualization.part_of}",
                type_of_criteria="contact",
                part_of="CONTACT",
                function=CriteriaFunction(
                    name="max",
                    param=MaxParameters(
                        data_vector=DataVector(
                            type="CONTACT",
                            ID=visualization.ID,
                            array=["(0, resultant_force)"],
                        )
                    ),
                ),
            )
        )
    return objects, visualizations, definitions, criteria


def create_node_kinematics_data_visualization(
    nodes: Mapping[str, int],
    quantities: Sequence[str],
) -> Tuple[List[DataVisualizationDefinition], List[dict]]:
    """Create Dynasaur visualizations for the requested node histories.

    Returns both the typed definitions used by the whiplash workflow and the
    serialized definitions written to the criteria procedure file.
    """
    visualizations = [
        DataVisualizationDefinition(
            name=f"{node_name}_{quantity}",
            part_of=node_name,
            type="NODE",
            ID=node_name,
            y=quantity,
            x="time",
        )
        for node_name in nodes for quantity in quantities
    ]
    definitions: List[dict] = []
    for visualization in visualizations:
        create_data_visualization(
            items=definitions,
            name=visualization.name,
            part_of=visualization.part_of,
            ID=visualization.ID,
            crit_type=visualization.type,
            x_crit=visualization.x,
            y_crit=visualization.y,
        )
    return visualizations, definitions


def create_segmental_angulation_data_visualization(
    nodes: Mapping[str, int],
) -> Tuple[List[DataVisualizationDefinition], List[dict]]:
    """Create Dynasaur subtraction visualizations for adjacent CoG nodes."""
    levels = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "T1"]
    cog_nodes: Dict[str, str] = {}
    for level in levels:
        pattern = re.compile(
            rf"(?:^|[-_]){re.escape(level)}(?:[-_]COG|COG)(?:$|[-_])",
            re.IGNORECASE,
        )
        node_name = next(
            (name for name in nodes if pattern.search(name)),
            None,
        )
        if node_name is not None:
            cog_nodes[level] = node_name

    visualizations: List[DataVisualizationDefinition] = []
    definitions: List[dict] = []
    part_of = "SEGMENTAL_ANGULATION"
    for first, second in zip(levels, levels[1:]):
        first_node = cog_nodes.get(first)
        second_node = cog_nodes.get(second)
        if first_node is None or second_node is None:
            continue
        segment = f"{first}-{second}"
        name = f"segmental_angulation{first}{second}"
        visualizations.append(
            DataVisualizationDefinition(
                name=name,
                part_of=part_of,
                type="NODE",
                ID=first_node,
                y=segment,
                x="time",
            )
        )
        definitions.append(
            {
                "name": name,
                "part_of": part_of,
                "x": {
                    "type": "NODE",
                    "ID": first_node,
                    "array": ["(0, time)"],
                },
                "y": {
                    "function": {
                        "name": "sub",
                        "param": {
                            "data_vector_1": {
                                "type": "NODE",
                                "ID": first_node,
                                "array": ["(0, ry_displacement)"],
                            },
                            "data_vector_2": {
                                "type": "NODE",
                                "ID": second_node,
                                "array": ["(0, ry_displacement)"],
                            },
                        },
                    }
                },
            }
        )
    return visualizations, definitions


def export_node_kinematics_data(
    simulation_files_dir: Union[Path, str],
    keyword_files: Sequence[Union[Path, str]],
    output_dir: Union[Path, str],
    quantities: Sequence[str],
) -> Path:
    """Export requested node time series from an LS-DYNA simulation.

    The keyword files provide the history-node names and IDs. The simulation
    directory must contain the matching ``binout*`` files.
    """
    requested_quantities = list(dict.fromkeys(quantities))
    if not requested_quantities:
        raise ValueError("At least one node measurement must be selected.")

    keyword_paths = [Path(path) for path in keyword_files]
    simulation_dir = Path(simulation_files_dir)
    destination = Path(output_dir)
    nodes: Dict[str, int] = {}
    for keyword_file in keyword_paths:
        cards = read_keywords(str(keyword_file))
        for keyword, lines in cards.items():
            if keyword.startswith("*DATABASE_HISTORY_NODE_ID"):
                nodes.update(get_dyna_history_node_id(list(lines)))
    if not nodes:
        raise ValueError(
            "No history nodes were found in the selected keyword files."
        )

    node_visualizations, definitions = create_node_kinematics_data_visualization(
        nodes,
        requested_quantities,
    )
    object_definition, criteria_definition = (
        write_node_kinematics_definition_files(
            simulation_dir=simulation_dir,
            nodes=nodes,
            data_visualization_definitions=definitions,
        )
    )

    controller = DataVisualizationController(
        calculation_procedure_def_file=str(criteria_definition),
        object_def_file=str(object_definition),
        data_source=str(simulation_dir / "binout*"),
    )
    for visualization in node_visualizations:
        controller.calculate(
            {
                "visualization": visualization.part_of + "_" + visualization.name,
                "x_label": visualization.x + " [ms]",
                "y_label": visualization.y,
            }
        )

    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / "whiplash_requested_node_measurements.csv"
    controller.write_CSV(str(destination), filename=output_path.name)
    return output_path


def write_node_kinematics_definition_files(
    simulation_dir: Union[Path, str],
    nodes: Mapping[str, int],
    data_visualization_definitions: Sequence[dict],
) -> Tuple[Path, Path]:
    """Write the object and criteria definitions consumed by Dynasaur."""
    simulation_path = Path(simulation_dir)
    object_definition = simulation_path / "object_definition_whiplash_nodes.def"
    criteria_definition = simulation_path / "criteria_definition_whiplash_nodes.def"
    write_object_file(
        dir=object_definition,
        objects=create_objects(type_obj="NODE", data=nodes),
    )
    write_criteria_file(
        dir=criteria_definition,
        data_visualization=data_visualization_definitions,
        criteria=[],
    )
    return object_definition, criteria_definition


def write_data_visualization_definition_file(
    simulation_dir: Union[Path, str],
    suffix: str,
    definitions: Sequence[dict],
) -> Path:
    """Write a calculation file containing only one visualization group."""
    definition_path = Path(simulation_dir) / f"criteria_definition_{suffix}.def"
    write_criteria_file(
        dir=definition_path,
        data_visualization=definitions,
        criteria=[],
    )
    return definition_path


def create_part_stress_criteria(
    parts: Mapping[str, int],
    part_of: str = "Neck",
    percentile: float = 0.5,
) -> List[CriteriaDefinition]:
    """Create percentile stress criteria for all keyword-defined parts.

    The part name is used as the Dynasaur object ID because it is also the
    name assigned by :func:`create_model_part_objects`.
    """
    return [
        CriteriaDefinition(
            name=part_name + "",
            type_of_criteria="injury",
            part_of=part_of,
            function=CriteriaFunction(
                name="percentile",
                param=PercentileParameters(
                    object_data=CriteriaParamObjectData(
                        type="OBJECT",
                        ID=part_name,
                        strain_stress="Strain",
                    ),
                    selection_tension_compression="Overall",
                    integration_point="Mean",
                    percentile=percentile,
                ),
            ),
        )
        for part_name in parts
    ]


def get_unresolved_criteria_objects(
    criteria: Sequence[CriteriaDefinition],
    objects: Sequence[dict],
) -> List[str]:
    """Return criterion object IDs absent from the generated object definitions."""
    object_names = {
        item["name"]
        for item in objects
        if item.get("type") == "OBJECT"
    }
    unresolved: List[str] = []
    for criterion in criteria:
        param = criterion.function.param
        if isinstance(param, PercentileParameters):
            object_id = param.object_data.ID
            if object_id not in object_names:
                unresolved.append(object_id)
    return unresolved


def main() -> Optional[Tuple[Path, Path, Path, Path]]:
    """Build Dynasaur definitions and evaluate whiplash criteria."""
    simulation_files_dir = choose_folder(
        "Select folder with simulation files and auxiliary files (def files)"
    )
    if not simulation_files_dir:
        return None

    keyword_files = choose_files(
        "Select keyword files (you can select multiple files)",
        filetypes=(("Keyword files", "*.k*"), ("All files", "*.*")),
    )
    if not keyword_files:
        return None

    output_dir = choose_folder("Select folder to save criteria CSV")
    if not output_dir:
        return None

    all_objects: List[dict] = []
    parts = read_model_parts([Path(path) for path in keyword_files])
    vivaplus_categories = read_vivaplus_categories()
    ligament_parts = select_vivaplus_parts(
        parts,
        vivaplus_categories,
        [LIGAMENT_CATEGORY],
    )
    energy_parts = select_vivaplus_parts(
        parts,
        vivaplus_categories,
        [FACET_JOINT_CATEGORY, INTERVERTEBRAL_DISC_CATEGORY],
    )
    all_objects.extend(create_model_part_objects(ligament_parts))
    part_energy_objects, part_energy_visualizations, part_energy_definitions = (
        create_part_energy_objects(
            energy_parts,
            {
                "intervertebral disc bodies": vivaplus_categories.get(
                    "intervertebral disc bodies", {}
                ),
                "articular processes": vivaplus_categories.get(
                    "articular processes", {}
                ),
            },
        )
    )
    all_objects.extend(part_energy_objects)
    criteria = create_part_stress_criteria(ligament_parts)
    node_visualizations: List[DataVisualizationDefinition] = []
    data_visualization_definitions: List[dict] = []
    nodes: Dict[str, int] = {}
    beams: Dict[str, int] = {}
    contacts: Dict[str, int] = {}
    simulation_dir = Path(simulation_files_dir)
    element_cards: Dict[str, Sequence[str]] = {}
    element_card_counters = {"shell": 0, "solid": 0}

    for keyword_file in keyword_files:
        cards = read_keywords(keyword_file)
        for keyword, lines in cards.items():
            if keyword == "*ELEMENT_SHELL" or keyword.startswith("*ELEMENT_SHELL_"):
                element_card_counters["shell"] += 1
                element_cards[
                    f"*ELEMENT_SHELL_{element_card_counters['shell']}"
                ] = lines
            elif keyword == "*ELEMENT_SOLID" or keyword.startswith("*ELEMENT_SOLID_"):
                element_card_counters["solid"] += 1
                element_cards[
                    f"*ELEMENT_SOLID_{element_card_counters['solid']}"
                ] = lines
        all_objects.extend(create_model_node_objects(cards))
        for keyword, lines in cards.items():
            if keyword.startswith("*DATABASE_HISTORY_NODE_ID"):
                nodes.update(get_dyna_history_node_id(list(lines)))
            elif keyword.startswith("*DATABASE_HISTORY_BEAM_ID"):
                beams.update(get_dyna_history_beam_id(list(lines)))
        contacts.update(get_dyna_contact(cards))

    if not beams:
        raise ValueError(
            "No *DATABASE_HISTORY_BEAM_ID entries were found in the selected "
            "keyword files."
        )

    get_elements(
        element_cards,
        pickle_path=simulation_dir / "element_connectivity.pkl",
    )

    cog_nodes = {
        node_name: node_id
        for node_name, node_id in nodes.items()
        if "COG" in node_name.upper()
    }
    node_visualizations, data_visualization_definitions = (
        create_node_kinematics_data_visualization(
            cog_nodes,
            ["x_coordinate", "z_coordinate", "ry_displacement"],
        )
    )
    segmental_visualizations, segmental_definitions = (
        create_segmental_angulation_data_visualization(cog_nodes)
    )
    node_visualizations.extend(segmental_visualizations)
    data_visualization_definitions.extend(segmental_definitions)
    beam_objects, beam_visualizations, beam_definitions = (
        create_beam_axial_data_visualization(beams)
    )
    all_objects.extend(beam_objects)
    (
        contact_objects,
        contact_visualizations,
        contact_definitions,
        contact_criteria,
    ) = create_contact_force_data_visualization(contacts)
    all_objects.extend(contact_objects)
    criteria.extend(contact_criteria)

    object_definition = simulation_dir / "object_definition_whiplash.def"
    criteria_definition = simulation_dir / "criteria_definition_whiplash.def"
    data_source = str(simulation_dir / "binout*")

    write_object_file(dir=object_definition, objects=all_objects)
    write_criteria_file(
        dir=criteria_definition,
        data_visualization=(
            data_visualization_definitions
            + part_energy_definitions
            + beam_definitions
            + contact_definitions
        ),
        criteria=criteria,
    )

    unresolved_objects = get_unresolved_criteria_objects(criteria, all_objects)
    if unresolved_objects:
        raise ValueError(
            "Criteria refer to parts missing from the object definition: "
            + ", ".join(unresolved_objects)
        )

    enable_rcforc_resultant_force()
    criteria_controller = CriteriaController(
        calculation_procedure_def_file=str(criteria_definition),
        object_def_file=str(object_definition),
        data_source=data_source,
    )
    skipped_criteria: List[str] = []
    for criterion in criteria:
        criterion_name = criterion.part_of + "_" + criterion.name
        try:
            criteria_controller.calculate({"criteria": criterion_name})
        except ValueError as error:
            if str(error) != "All-NaN slice encountered":
                raise
            skipped_criteria.append(criterion_name)
            print(
                "Warning: skipped criterion with no finite binout data: "
                + criterion_name
            )
    criteria_controller.write_CSV(output_dir, filename="whiplash_criteria.csv")
    if skipped_criteria:
        print(
            "Whiplash analysis completed with skipped criteria: "
            + ", ".join(skipped_criteria)
        )

    node_definition = write_data_visualization_definition_file(
        simulation_dir,
        "whiplash_nodes",
        data_visualization_definitions,
    )
    data_visualization_controller = DataVisualizationController(
        calculation_procedure_def_file=str(node_definition),
        object_def_file=str(object_definition),
        data_source=data_source,
    )
    for visualization in node_visualizations:
        y_label = (
            visualization.y
            if visualization.part_of == "SEGMENTAL_ANGULATION"
            else visualization.y + " [mm]"
        )
        data_visualization_controller.calculate(
            {
                "visualization": visualization.part_of + "_" + visualization.name,
                "x_label": visualization.x + " [ms]",
                "y_label": y_label,
            }
        )
    node_csv_path = simulation_dir / "whiplash_node_trajectories.csv"
    data_visualization_controller.write_CSV(
        str(simulation_dir),
        filename=node_csv_path.name,
    )
    part_energy_definition = write_data_visualization_definition_file(
        simulation_dir,
        "whiplash_part_energy",
        part_energy_definitions,
    )
    part_energy_controller = DataVisualizationController(
        calculation_procedure_def_file=str(part_energy_definition),
        object_def_file=str(object_definition),
        data_source=data_source,
    )
    for visualization in part_energy_visualizations:
        part_energy_controller.calculate(
            {
                "visualization": visualization.part_of + "_" + visualization.name,
                "x_label": visualization.x + " [ms]",
                "y_label": visualization.y + " [J]",
            }
        )
    part_energy_csv_path = simulation_dir / "whiplash_part_energies.csv"
    part_energy_controller.write_CSV(
        str(simulation_dir),
        filename=part_energy_csv_path.name,
    )
    beam_definition = write_data_visualization_definition_file(
        simulation_dir,
        "whiplash_beams",
        beam_definitions,
    )
    beam_controller = DataVisualizationController(
        calculation_procedure_def_file=str(beam_definition),
        object_def_file=str(object_definition),
        data_source=data_source,
    )
    for visualization in beam_visualizations:
        beam_controller.calculate(
            {
                "visualization": visualization.part_of + "_" + visualization.name,
                "x_label": visualization.x + " [ms]",
                "y_label": visualization.y,
            }
        )
    beam_csv_path = simulation_dir / "whiplash_beam_axial.csv"
    beam_controller.write_CSV(
        str(simulation_dir),
        filename=beam_csv_path.name,
    )
    if not beam_csv_path.is_file():
        raise OSError(f"Beam axial CSV was not created: {beam_csv_path}")
    if contact_visualizations:
        contact_definition = write_data_visualization_definition_file(
            simulation_dir,
            "whiplash_contacts",
            contact_definitions,
        )
        contact_controller = DataVisualizationController(
            calculation_procedure_def_file=str(contact_definition),
            object_def_file=str(object_definition),
            data_source=data_source,
        )
        for visualization in contact_visualizations:
            contact_controller.calculate(
                {
                    "visualization": visualization.part_of + "_" + visualization.name,
                    "x_label": visualization.x + " [ms]",
                    "y_label": visualization.y,
                }
            )
        contact_csv_path = simulation_dir / "whiplash_contact_forces.csv"
        contact_controller.write_CSV(
            str(simulation_dir),
            filename=contact_csv_path.name,
        )
        if not contact_csv_path.is_file():
            raise OSError(f"Contact force CSV was not created: {contact_csv_path}")
    return (
        node_csv_path,
        Path(output_dir) / "whiplash_criteria.csv",
        part_energy_csv_path,
        beam_csv_path,
    )


if __name__ == "__main__":
    main()