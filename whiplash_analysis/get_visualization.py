
def get_cells(dr, p, points_with_id, shells):
    """
    Extracts the cell connectivity information for shell elements at a specific time step and integration point from a D3plotReader object.

    Parameters:
    dr (D3plotReader): An instance of the D3plotReader class containing the simulation data.
    p (D3P_Parameter): A parameter object specifying the timestep and integration point.
    points_with_id (dict): A dictionary mapping node IDs to their coordinates.

    Returns:
    cells_vtk: A 1D array containing the cell connectivity information formatted for VTK.
    cell_types_single: A 1D array containing the VTK cell type for each cell
    """
    #Libraries
    import numpy as np
    import lsreader as lr
    import sys
    import os
    from pathlib import Path
    import pyvista as pv

    #Import the paths
    current_dir = Path(__file__).resolve().parent
    upper_dir = current_dir.parent
    sys.path.append(str(upper_dir))
    from core.io.directories_files import nodes_dir
    from core.io.keyword_reader import read_keywords as kr
    from get_elements_from_keyword import get_elements_from_keyword as shells_from_keyword
    n_shells = shells.shape[0]
    # Map LS-DYNA node IDs to VTK point indices
    unique_ls_ids = np.array(list(points_with_id.keys()))
    vtk_indices = np.arange(len(unique_ls_ids), dtype=np.int64)
    shell_conn_vtk = np.searchsorted(unique_ls_ids, shells.flatten(), side='left')


    test_text = open(os.path.join(current_dir, 'test_shells.txt'), 'w')
    test_text.write("Shells: \n")
    #for i in range(1000):
        #test_text.write(str(shells[i]) + "\n")

    shell_conn_vtk = shell_conn_vtk.reshape(-1, 4)  # Reshape to (n_shells, 4)
    test_text.write("Shells_vtk: \n")
    #for i in range(1000):
        #test_text.write(str(shell_conn_vtk[i]) + "\n")

    # Detect types: QUAD (4 unique), TRIA (3 unique, node3==node4)
    unique_counts = np.array([
    len(np.unique(row[row != 0]))
    for row in shell_conn_vtk
    ])

    n_quads = np.sum(unique_counts == 4)
    n_tris = np.sum(unique_counts == 3)

    for row in range(shell_conn_vtk.shape[0]):
        if unique_counts[row] == 3:
            shell_conn_vtk[row, 3] = 0  # Set last node to 0 for tris
    test_text.write("Shells_vtk after setting tris: \n")
    for i in range(shell_conn_vtk.shape[0]):
        test_text.write(str(shell_conn_vtk[i]) + "\n")
    
    # Create VTK cell array: [num_nodes, node1, node2, node3, node4]
    cells = np.hstack([np.full((n_shells, 1), 4, dtype=np.int64), shell_conn_vtk])
    for i, row in enumerate(shell_conn_vtk):
        if row[-1] == 0: 
            cells[i, 0] = 3  # Ensure first cell value is 3 for tri elements
    cells_vtk = []
    for i in range(len(cells)):
        cell = cells[i]
        if cell[0] == 3:  # Tria
            cells_vtk.extend(cell[:4])  # 3 elems (node1,node2,node3)
        elif cell[0] == 4:  # Quad
            cells_vtk.extend(cell[:5])   # 4 nodes
    cells_vtk = np.array(cells_vtk)
    #Define cell types: 9 for QUAD, 5 for TRI
    cell_types = np.empty((n_shells, 5), dtype=np.uint8)
    cell_types[:, 0] = 4  # Initialize all rows with 4 (QUAD)
    cell_types[unique_counts == 3, 0] = 3  # Set tri elements to 3
    cell_types[:, 1:] = pv.CellType.QUAD      # Fill remaining columns with QUAD type (9)
    cell_types[unique_counts == 3, 1:] = pv.CellType.TRIANGLE  # Fill tri rows with TRIANGLE type (5)
    cell_types_single = np.array([cell[1] for cell in cell_types])
    test_text.write( "cell_types: \n")

    test_text.close()
    return cells_vtk, cell_types_single

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
    from core.io.keyword_reader import read_keywords as kr
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

def get_points(dr, p):
    """
    Extracts the coordinates of the nodes at a specific time step and integration point from a D3plotReader object.

    Parameters:
    dr (D3plotReader): An instance of the D3plotReader class containing the simulation data.
    p (D3P_Parameter): A parameter object specifying the timestep and integration point.

    Returns:
    np.ndarray: A 2D array of shape (num_nodes, 3) containing the x, y, z coordinates of each node.
    """
    import numpy as np
    import lsreader as lr
    nodes_disp = dr.get_data(lr.DataType.D3P_NODE_COORDINATES, ist=p.ist, ipt=p.ipt)
    id_obj = dr.get_data(lr.DataType.D3P_NODE_IDS, ist=p.ist, ipt=p.ipt)
    id = np.array([id for id in id_obj])
    x_coords = np.array([vec.x() for vec in nodes_disp])
    y_coords = np.array([vec.y() for vec in nodes_disp])
    z_coords = np.array([vec.z() for vec in nodes_disp])
    
    points = np.column_stack([x_coords, y_coords, z_coords])
    points_with_id = {id[i]: points[i] for i in range(len(id))}
    return points, points_with_id