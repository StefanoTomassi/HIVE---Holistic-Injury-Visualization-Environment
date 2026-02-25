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