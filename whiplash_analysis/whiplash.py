"""Whiplash model input discovery."""

from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Union

from dynasaur.plugins.criteria_controller import CriteriaController

from core.dataclasses.simulation_dataclasses import (
    CriteriaDefinition,
    CriteriaFunction,
    CriteriaParamObjectData,
    PercentileParameters,
)
from core.io.create_criteria import write_criteria_file
from core.io.create_objects import create_objects, write_object_file
from core.io.keyword_reader import (
    get_dyna_history_node_id,
    get_dyna_parts,
    read_keywords,
)
from core.io.select_folder import choose_files, choose_folder


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
            name=part_name + "_stress",
            type_of_criteria="injury",
            part_of=part_of,
            function=CriteriaFunction(
                name="percentile",
                param=PercentileParameters(
                    object_data=CriteriaParamObjectData(
                        type="OBJECT",
                        ID=part_name,
                        strain_stress="Stress",
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
    return [
        criterion.function.param.object_data.ID
        for criterion in criteria
        if criterion.function.param.object_data.ID not in object_names
    ]


def main() -> None:
    """Build Dynasaur definitions and evaluate whiplash criteria."""
    simulation_files_dir = choose_folder(
        "Select folder with simulation files and auxiliary files (def files)"
    )
    if not simulation_files_dir:
        return

    keyword_files = choose_files(
        "Select keyword files (you can select multiple files)",
        filetypes=(("Keyword files", "*.k*"), ("All files", "*.*")),
    )
    if not keyword_files:
        return

    output_dir = choose_folder("Select folder to save criteria CSV")
    if not output_dir:
        return

    all_objects: List[dict] = []
    parts = read_model_parts([Path(path) for path in keyword_files])
    all_objects.extend(create_model_part_objects(parts))
    criteria = create_part_stress_criteria(parts)

    for keyword_file in keyword_files:
        cards = read_keywords(keyword_file)
        all_objects.extend(create_model_node_objects(cards))

    simulation_dir = Path(simulation_files_dir)
    object_definition = simulation_dir / "object_definition_whiplash.def"
    criteria_definition = simulation_dir / "criteria_definition_whiplash.def"
    data_source = str(simulation_dir / "binout*")

    write_object_file(dir=object_definition, objects=all_objects)
    write_criteria_file(
        dir=criteria_definition,
        data_visualization=[],
        criteria=criteria,
    )

    unresolved_objects = get_unresolved_criteria_objects(criteria, all_objects)
    if unresolved_objects:
        raise ValueError(
            "Criteria refer to parts missing from the object definition: "
            + ", ".join(unresolved_objects)
        )

    criteria_controller = CriteriaController(
        calculation_procedure_def_file=str(criteria_definition),
        object_def_file=str(object_definition),
        data_source=data_source,
    )
    for criterion in criteria:
        criteria_controller.calculate(
            {"criteria": criterion.part_of + "_" + criterion.name}
        )
    criteria_controller.write_CSV(output_dir, filename="whiplash_criteria.csv")


if __name__ == "__main__":
    main()