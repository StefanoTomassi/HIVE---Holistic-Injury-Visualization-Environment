import json
from pathlib import Path
from typing import List, Mapping, Union


def create_objects(type_obj: str, data: Mapping[str, Union[str, int]]) -> List[dict]:
    """"
    Writes node IDs and names to 'history_node_id.def' file and returns a dictionary mapping node names to IDs.
    Args:
        dir (str): Directory path where the file will be saved.
        nodes (list): List of strings, each containing a node ID and name separated by space and coming from the keyword_reader parser.
        Returns:
            dict: A dictionary where keys are node names and values are node IDs.
    """
    objects = []
    for name, object_id in data.items():
        objects.append({
            "type": type_obj,
            "name": name,
            "id": [int(object_id)]
        })
    return objects


def write_object_file(dir: Union[Path, str], objects: List[dict]) -> None:
    """
    Writes the list of objects to the objects .def file in JSON format needed for dynasaur to evaluate
    the outputs.
    Args:
        dir (str): Directory path where the file will be saved.
        objects (list): A list of dictionaries, each representing an object with its type, name, and ID.
    """
    first_order = {
        "OBJECTS": objects
    }

    with Path(dir).open("w", encoding="utf-8") as f:
        json.dump(first_order, f, indent=2)
