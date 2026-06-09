from importlib.resources import path
import os
import json

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
    

        
def write_criteria_file(dir: path, data_visualization: list, criteria: list):
    first_order = []
    first_order.append({
        "UNIT": {
            "time": "ms",
            "length": "mm",
            "mass": "kg"
        }})
    first_order.append({
        "CRITERIA": criteria
    })
    first_order.append({
        "DATA VISUALIZATION": data_visualization
    })

    with open(dir, 'w', encoding="utf-8") as f:
        json.dump(first_order, f, indent=2)