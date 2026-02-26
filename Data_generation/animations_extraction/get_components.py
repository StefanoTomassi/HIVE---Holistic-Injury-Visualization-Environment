def get_component(points_with_id, shells, parts, selected_part):
    """
    Extracts the component IDs for each cell based on the node connectivity and cell types.

    Parameters:
    points_with_id (dict): A dictionary mapping LS-DYNA node IDs to their coordinates.
    shells (numpy.ndarray): An array of shell element node connectivity.
    cell_types (numpy.ndarray): An array of cell types corresponding to each shell element.

    Returns:
    numpy.ndarray: An array of component IDs for each cell.
    """
    import numpy as np
    import os
    from pathlib import Path
    current_dir = Path(__file__).resolve().parent
    for key in parts.keys():
        if parts[key] == selected_part:
            part_id_desired = key
            break
    shells_in_part = [0,0,0,0,0,0]
    for shell in shells:
        part_id = shell[1]
        if part_id == part_id_desired:
            shells_in_part = np.vstack([shells_in_part, shell])
    nodes_with_id = {}
    for point in points_with_id.keys():
        if point in shells_in_part[:, 2:6].flatten():
            if point not in nodes_with_id:
                nodes_with_id[point] = points_with_id[point]
    shells_in_part = shells_in_part[1:]
    shells_in_part = shells_in_part[:, 2:6]
    nodes = []
    for node in nodes_with_id:
        nodes.append(nodes_with_id[node])
    nodes = np.array(nodes)
    return shells_in_part, nodes, nodes_with_id