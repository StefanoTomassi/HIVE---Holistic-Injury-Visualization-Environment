import os
import json
from importlib.resources import path

def create_objects(type_obj: str, data: dict) -> list :
    """"
    Writes node IDs and names to 'history_node_id.def' file and returns a dictionary mapping node names to IDs.
    Args:
        dir (str): Directory path where the file will be saved.
        nodes (list): List of strings, each containing a node ID and name separated by space and coming from the keyword_reader parser.
        Returns:
            dict: A dictionary where keys are node names and values are node IDs.
    """
    objects = []
    for part, id in data.items():
        objects.append({
            "type": type_obj,
            "name": part,
            "id": [int(id)]
        })
    return objects

def write_object_file(dir: path, objects: list):
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

    with open(dir, 'a', encoding="utf-8") as f:
        json.dump(first_order, f, indent=2)
