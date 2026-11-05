"""Generate Dynasaur object definitions from LS-DYNA keyword files."""

from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Union

from core.io.create_objects import create_objects, write_object_file
from core.io.keyword_reader import get_dyna_history_node_id, read_keywords
from core.io.select_folder import choose_file


PathLike = Union[Path, str]


def read_history_nodes(
    keyword_files: Union[PathLike, Sequence[PathLike]],
) -> Dict[str, int]:
    """Read history-node names and IDs from LS-DYNA keyword files.

    Args:
        keyword_files: One keyword file or a sequence of keyword files.

    Returns:
        A mapping from Dynasaur node-object names to LS-DYNA node IDs.

    Raises:
        ValueError: If no ``*DATABASE_HISTORY_NODE_ID`` entries are found.
    """
    if isinstance(keyword_files, (str, Path)):
        files = [keyword_files]
    else:
        files = list(keyword_files)

    nodes: Dict[str, int] = {}
    for keyword_file in files:
        cards = read_keywords(str(keyword_file))
        for keyword, lines in cards.items():
            if keyword.startswith("*DATABASE_HISTORY_NODE_ID"):
                parsed_nodes = get_dyna_history_node_id(list(lines))
                nodes.update(
                    {
                        node_name: int(node_id)
                        for node_name, node_id in parsed_nodes.items()
                    }
                )

    if not nodes:
        raise ValueError(
            "No *DATABASE_HISTORY_NODE_ID entries were found in the selected "
            "keyword files."
        )
    return nodes


def create_node_objects(nodes: Mapping[str, int]) -> List[dict]:
    """Create Dynasaur ``NODE`` objects from a node name-to-ID mapping."""
    if not nodes:
        raise ValueError("At least one history node is required.")
    return create_objects(type_obj="NODE", data=nodes)


def create_node_objects_from_keywords(
    keyword_files: Union[PathLike, Sequence[PathLike]],
) -> List[dict]:
    """Read keyword files and create their Dynasaur ``NODE`` objects."""
    return create_node_objects(read_history_nodes(keyword_files))


def write_node_object_definition(
    keyword_files: Union[PathLike, Sequence[PathLike]],
    output_file: PathLike,
) -> Path:
    """Read history nodes and write a Dynasaur object-definition file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_object_file(
        dir=output_path,
        objects=create_node_objects_from_keywords(keyword_files),
    )
    return output_path


def main() -> None:
    """Interactively create a node object-definition file."""
    keyword_file = choose_file(
        "Select keyword file",
        filetypes=(("Keyword files", "*.k*"), ("All files", "*.*")),
    )
    if not keyword_file:
        return

    keyword_path = Path(keyword_file)
    output_file = keyword_path.with_name("object_definition_nodes.def")
    write_node_object_definition(keyword_path, output_file)
    print(f"Node object definition written to {output_file}")


if __name__ == "__main__":
    main()