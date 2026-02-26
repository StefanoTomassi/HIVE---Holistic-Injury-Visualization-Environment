def get_elements_from_keyword(nodes_dir, part_dir):
    """
    Extracts shell element connectivity information from a keyword file.

    Parameters:
    nodes_dir (str): The path to the directory containing the keyword file.

    Returns:
    shells (numpy.ndarray): An array of shell element node connectivity.
    n_shells (int): The number of shell elements.
    """    
    #Libraries
    import numpy as np
    import sys
    import os
    
    from pathlib import Path
    current_dir = Path(__file__).resolve().parent
    upper_dir = current_dir.parent
    sys.path.append(str(upper_dir))
    from keyword_reader import read_keywords as kr
    keyword_nodes = kr(nodes_dir)
    keyword_parts = kr(part_dir)
    shells = np.array([0, 0, 0, 0, 0, 0], dtype=np.int64)
    for key in keyword_nodes.keys():
        if '*ELEMENT_SHELL' in key:
            for line in keyword_nodes[key]:
                line = line.strip().split(' ')
                id_el = int(line[0])
                nodes_part = int(line[1])
                nodes = [int(node) for node in line[2:6]]
                node_info = np.hstack([id_el, nodes_part, nodes])
                shells = np.vstack([shells, node_info])
    parts = {}
    for key in keyword_parts.keys():
        if '*PART' in key:
            filtered_lines = [line for line in keyword_parts[key] if not line.strip().startswith(('$', '*COMMENT'))]
            filtered_lines = np.array([line.strip() for line in filtered_lines])
            part_name = filtered_lines[0]
            part_id = int(filtered_lines[1].strip()[0:10])
            parts[part_id] = part_name
    shells = shells[1:]  # Remove the initial placeholder row
    return shells, parts