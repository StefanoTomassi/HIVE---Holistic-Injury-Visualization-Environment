def get_cells(dr, p, points_with_id):
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
    from directories_files import nodes_dir
    from keyword_reader import read_keywords as kr

    #Read the keyword file and extract the shell connectivity
    keywords = kr(nodes_dir)
    shells = np.array([0, 0, 0, 0], dtype=np.int64)
    for key in keywords.keys():
        if '*ELEMENT_SHELL' in key:
            for line in keywords[key]:
                line = line.strip().split(' ')
                id_el = int(line[0])
                nodes = [int(node) for node in line[2:6]]
                shells = np.vstack([shells, nodes])


    shells = shells[1:]  # Remove the initial placeholder row
    n_shells = shells.shape[0]  # Assuming 4 nodes/shell

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
    test_text.write("Cells VTK: \n")
    for i in range(1000):        test_text.write(str(cells_vtk[i]) + "\n")
    print("Cells VTK shape:", cells_vtk.shape)
    #Define cell types: 9 for QUAD, 5 for TRI
    cell_types = np.empty((n_shells, 5), dtype=np.uint8)
    cell_types[:, 0] = 4  # Initialize all rows with 4 (QUAD)
    cell_types[unique_counts == 3, 0] = 3  # Set tri elements to 3
    cell_types[:, 1:] = pv.CellType.QUAD      # Fill remaining columns with QUAD type (9)
    cell_types[unique_counts == 3, 1:] = pv.CellType.TRIANGLE  # Fill tri rows with TRIANGLE type (5)
    cell_types_single = np.array([cell[1] for cell in cell_types])
    test_text.write( "cell_types: \n")
    for i in range(1000):
        test_text.write(str(cell_types_single[i]) + "\n")

    test_text.close()
    return cells_vtk, cell_types_single