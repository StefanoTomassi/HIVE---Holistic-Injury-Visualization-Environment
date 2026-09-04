import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Union

def create_data_visualization(items: list, name: str, part_of: str, ID: str, crit_type: str, x_crit: str, y_crit: str):
    items.append({
        "name": name,
        "part_of": part_of,
        "y": {
            "type": crit_type,
            "ID": ID,
            "array": [f"(0, {y_crit})"]
        },
        "x": {
            "type": crit_type,
            "ID": ID,
            "array": [f"(0, {x_crit})"]
        }
    })

def create_criteria(nodes: dict, crit_type: str, x_crit: str, y_crit: str) -> list:
    criteria_list = []
    

        
def write_criteria_file(
    dir: Union[Path, str],
    data_visualization: Iterable[Any],
    criteria: Iterable[Any],
) -> None:
    """Write criteria and visualization definitions for Dynasaur.

    Dataclass definitions are converted to dictionaries before serialization.
    Existing dictionary-based definitions remain supported.
    """
    serialized_criteria = [
        asdict(item) if is_dataclass(item) else item for item in criteria
    ]
    serialized_visualizations = [
        asdict(item) if is_dataclass(item) else item for item in data_visualization
    ]
    first_order = []
    first_order.append({
        "UNIT": {
            "time": "ms",
            "length": "mm",
            "mass": "kg"
        }})
    first_order.append({
        "CRITERIA": serialized_criteria
    })
    first_order.append({
        "DATA VISUALIZATION": serialized_visualizations
    })

    with Path(dir).open("w", encoding="utf-8") as f:
        json.dump(first_order, f, indent=2)