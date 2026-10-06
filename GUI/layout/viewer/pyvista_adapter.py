import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import plotly.graph_objects as go
import pyvista as pv

from core.io.find_simulation_files import find_output_simulation_files


def _read_coordinates(d3plot_path: str, timestep: int) -> np.ndarray:
    """Read one LS-DYNA coordinate state as an ``(n, 3)`` array."""
    import lsreader as lr

    reader = lr.D3plotReader(d3plot_path)
    try:
        vectors = reader.get_data(
            lr.DataType.D3P_NODE_COORDINATES,
            ist=timestep,
            ipt=0,
        )
        return np.asarray([[item.x(), item.y(), item.z()] for item in vectors])
    finally:
        reader.close()


def _read_shell_connectivity(
    d3plot_path: str, node_ids: np.ndarray, num_shells: int
) -> np.ndarray:
    """Read shell connectivity and return LS-DYNA node IDs per element."""
    import lsreader as lr

    reader = lr.D3plotReader(d3plot_path)
    try:
        connectivity = None
        for data_type in (
            lr.DataType.D3P_SHELL_ID_CONNECTIVITY_MAT,
            lr.DataType.D3P_SHELL_CONNECTIVITY_MAT,
        ):
            try:
                raw_connectivity = reader.get_data(
                    data_type,
                    ist=0,
                    ipt=0,
                    ask_for_numpy_array=True,
                )
            except (AttributeError, IndexError, RuntimeError, TypeError, ValueError):
                continue
            candidate = np.asarray(raw_connectivity, dtype=np.int64)
            if candidate.ndim == 2 and candidate.shape[1] >= 4:
                connectivity = candidate
                break
    finally:
        reader.close()
    if connectivity is None:
        raise ValueError("The d3plot file contains no shell connectivity data.")
    if connectivity.ndim == 1:
        if num_shells < 1 or connectivity.size % num_shells:
            raise ValueError("The shell connectivity data has an invalid shape.")
        connectivity = connectivity.reshape(num_shells, -1)
    if connectivity.ndim != 2 or connectivity.shape[1] < 4:
        raise ValueError("The shell connectivity data has an invalid shape.")

    known_nodes = set(int(node_id) for node_id in node_ids)
    best_nodes = None
    best_score = -1
    for offset in range(connectivity.shape[1] - 3):
        candidate = connectivity[:, offset : offset + 4]
        valid_values = np.vectorize(lambda value: int(value) in known_nodes)(candidate)
        score = int(valid_values.sum())
        if score > best_score:
            best_score = score
            best_nodes = candidate
    if best_nodes is not None and best_score > 0:
        valid = best_nodes[:, 0] > 0
        return best_nodes[valid]

    # Some lsreader builds expose connectivity as zero- or one-based internal
    # node indices rather than the user node IDs returned by D3P_NODE_IDS.
    node_count = len(node_ids)
    best_score = -1
    for offset in range(connectivity.shape[1] - 3):
        candidate = connectivity[:, offset : offset + 4]
        zero_based = np.logical_and(candidate >= 0, candidate < node_count)
        one_based = np.logical_and(candidate >= 1, candidate <= node_count)
        zero_based_score = int(zero_based.sum())
        one_based_score = int(one_based.sum())
        score = max(zero_based_score, one_based_score)
        if score > best_score:
            best_score = score
            best_nodes = candidate
    if best_nodes is None or best_score < 3:
        raise ValueError(
            "Could not identify shell node connectivity in the d3plot data."
        )
    if np.logical_and(best_nodes >= 1, best_nodes <= node_count).sum() >= np.logical_and(
        best_nodes >= 0, best_nodes < node_count
    ).sum():
        indices = best_nodes - 1
    else:
        indices = best_nodes
    valid = np.logical_and(indices >= 0, indices < node_count).all(axis=1)
    return node_ids[indices[valid]]


def _load_element_connectivity(
    connectivity_pickle_path: str,
) -> Tuple[
    Dict[int, Tuple[int, ...]],
    Dict[int, Tuple[int, ...]],
    Dict[int, int],
    Dict[int, int],
]:
    """Load shell and solid connectivity dictionaries from a pickle file."""
    path = Path(connectivity_pickle_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Connectivity pickle not found: {path}")
    with path.open("rb") as stream:
        payload = pickle.load(stream)
    if not isinstance(payload, dict):
        raise ValueError("Connectivity pickle must contain a dictionary.")
    try:
        shell_elements = payload["shell_elements"]
        solid_elements = payload["solid_elements"]
    except KeyError as error:
        raise ValueError(
            "Connectivity pickle must contain shell_elements and solid_elements."
        ) from error
    if not isinstance(shell_elements, dict) or not isinstance(solid_elements, dict):
        raise ValueError("Connectivity entries must be dictionaries.")
    try:
        shell_parts = payload["shell_parts"]
        solid_parts = payload["solid_parts"]
    except KeyError as error:
        raise ValueError(
            "Connectivity pickle must contain shell_parts and solid_parts. "
            "Regenerate it with get_elements()."
        ) from error
    if not isinstance(shell_parts, dict) or not isinstance(solid_parts, dict):
        raise ValueError("Part entries must be dictionaries.")

    def normalize(
        elements: Dict[object, object], expected_nodes: int
    ) -> Dict[int, Tuple[int, ...]]:
        normalized: Dict[int, Tuple[int, ...]] = {}
        for element_id, nodes in elements.items():
            if not isinstance(nodes, (tuple, list)) or len(nodes) != expected_nodes:
                raise ValueError(
                    f"Element {element_id} must contain {expected_nodes} node IDs."
                )
            normalized[int(element_id)] = tuple(int(node_id) for node_id in nodes)
        return normalized

    normalized_shell = normalize(shell_elements, 4)
    normalized_solid = normalize(solid_elements, 8)
    normalized_shell_parts = {
        int(element_id): int(part_id) for element_id, part_id in shell_parts.items()
    }
    normalized_solid_parts = {
        int(element_id): int(part_id) for element_id, part_id in solid_parts.items()
    }
    if not set(normalized_shell).issubset(normalized_shell_parts):
        raise ValueError("Connectivity pickle is missing shell element part IDs.")
    if not set(normalized_solid).issubset(normalized_solid_parts):
        raise ValueError("Connectivity pickle is missing solid element part IDs.")
    return (
        normalized_shell,
        normalized_solid,
        normalized_shell_parts,
        normalized_solid_parts,
    )


def _create_polygon_mesh(
    points: np.ndarray,
    shell_nodes: np.ndarray,
    node_index: Dict[int, int],
    solid_nodes: Optional[np.ndarray] = None,
) -> pv.PolyData:
    """Create a PyVista polygon mesh from shell and solid connectivity."""
    cells = []
    for nodes in shell_nodes:
        indices = [
            node_index[int(node_id)] for node_id in nodes if node_id > 0
        ]
        if len(indices) >= 3:
            cells.extend((len(indices), *indices))
    for nodes in solid_nodes if solid_nodes is not None else []:
        faces = (
            (nodes[0], nodes[1], nodes[2], nodes[3]),
            (nodes[4], nodes[5], nodes[6], nodes[7]),
            (nodes[0], nodes[1], nodes[5], nodes[4]),
            (nodes[1], nodes[2], nodes[6], nodes[5]),
            (nodes[2], nodes[3], nodes[7], nodes[6]),
            (nodes[3], nodes[0], nodes[4], nodes[7]),
        )
        for face in faces:
            indices = [node_index[int(node_id)] for node_id in face]
            cells.extend((4, *indices))
    if not cells:
        raise ValueError("The d3plot file contains no valid shell elements.")
    return pv.PolyData(points, np.asarray(cells, dtype=np.int64))


def _plotly_faces(mesh: pv.PolyData) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fan-triangulate PyVista polygons for Plotly Mesh3d serialization."""
    faces = mesh.faces
    triangles: List[Tuple[int, int, int]] = []
    cursor = 0
    while cursor < len(faces):
        count = int(faces[cursor])
        polygon = [int(index) for index in faces[cursor + 1 : cursor + 1 + count]]
        triangles.extend(
            (polygon[0], polygon[index], polygon[index + 1])
            for index in range(1, len(polygon) - 1)
        )
        cursor += count + 1
    if not triangles:
        raise ValueError("The d3plot file contains no renderable shell faces.")
    triangle_array = np.asarray(triangles, dtype=np.int64)
    return (
        triangle_array[:, 0],
        triangle_array[:, 1],
        triangle_array[:, 2],
    )


def _triangle_colors(
    polygon_part_ids: List[int],
    polygon_sizes: List[int],
) -> List[str]:
    """Assign one stable color to every rendered polygon."""
    palette = (
        "#0173b2", "#de8f05", "#029e73", "#d55e00",
        "#cc78bc", "#ca9161", "#56b4e9", "#f0e442",
    )
    colors = {
        part_id: palette[index % len(palette)]
        for index, part_id in enumerate(sorted(set(polygon_part_ids)))
    }
    return [
        colors[part_id]
        for part_id, size in zip(polygon_part_ids, polygon_sizes)
        for _ in range(size - 2)
    ]


def _create_animation_figure(
    folder: str,
    connectivity_pickle_path: Optional[str] = None,
    state_stride: int = 2,
) -> go.Figure:
    """Create an interactive mesh animation figure from a d3plot folder."""
    import lsreader as lr

    _, d3plots = find_output_simulation_files(folder)
    if not d3plots:
        raise FileNotFoundError(f"No d3plot files found in {folder}")
    d3plot_path = d3plots[0]
    reader = lr.D3plotReader(d3plot_path)
    try:
        num_states = int(reader.get_data(lr.DataType.D3P_NUM_STATES))
        node_ids = np.asarray(
            reader.get_data(
                lr.DataType.D3P_NODE_IDS,
                ist=0,
                ipt=0,
                ask_for_numpy_array=True,
            ),
            dtype=np.int64,
        ).reshape(-1)
    finally:
        reader.close()
    if num_states < 1:
        raise ValueError("The d3plot file contains no animation states.")

    if connectivity_pickle_path is None:
        connectivity_pickle_path = str(Path(folder) / "element_connectivity.pkl")
    (
        shell_elements,
        solid_elements,
        shell_parts,
        solid_parts,
    ) = _load_element_connectivity(connectivity_pickle_path)
    shell_nodes = np.asarray(list(shell_elements.values()), dtype=np.int64)
    solid_nodes = np.asarray(list(solid_elements.values()), dtype=np.int64)
    shell_polygon_part_ids = []
    shell_polygon_sizes = []
    for element_id, nodes in shell_elements.items():
        size = sum(node_id > 0 for node_id in nodes)
        if size >= 3:
            shell_polygon_part_ids.append(shell_parts[element_id])
            shell_polygon_sizes.append(size)
    polygon_part_ids = shell_polygon_part_ids + [
        solid_parts[element_id]
        for element_id in solid_elements
        for _ in range(6)
    ]
    polygon_sizes = shell_polygon_sizes + [4] * (6 * len(solid_elements))
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    try:
        first_points = _read_coordinates(d3plot_path, 0)
        mesh = _create_polygon_mesh(
            first_points,
            shell_nodes,
            node_index,
            solid_nodes if len(solid_nodes) else None,
        )
        i, j, k = _plotly_faces(mesh)
        face_colors = _triangle_colors(polygon_part_ids, polygon_sizes)
    except KeyError as error:
        raise ValueError("Shell connectivity references an unknown node.") from error

    state_indices = range(0, num_states, max(1, state_stride))
    frames = []
    for timestep in state_indices:
        points = _read_coordinates(d3plot_path, timestep)
        frames.append(
            go.Frame(
                name=str(timestep),
                data=[
                    go.Mesh3d(
                        x=points[:, 0],
                        y=points[:, 1],
                        z=points[:, 2],
                        i=i,
                        j=j,
                        k=k,
                        facecolor=face_colors,
                        opacity=0.9,
                        flatshading=True,
                        hoverinfo="skip",
                    )
                ],
            )
        )
    if not frames:
        raise RuntimeError("No animation states were loaded.")

    figure = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=go.Layout(
            scene={
                "aspectmode": "data",
                "xaxis": {"visible": False, "showgrid": False, "showticklabels": False},
                "yaxis": {"visible": False, "showgrid": False, "showticklabels": False},
                "zaxis": {"visible": False, "showgrid": False, "showticklabels": False},
            },
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            updatemenus=[
                {
                    "type": "buttons",
                    "showactive": False,
                    "x": 0.05,
                    "y": 0.05,
                    "buttons": [
                        {
                            "label": "Play",
                            "method": "animate",
                            "args": [
                                None,
                                {
                                    "frame": {"duration": 80, "redraw": True},
                                    "fromcurrent": True,
                                },
                            ],
                        }
                    ],
                }
            ],
            sliders=[
                {
                    "currentvalue": {"prefix": "State: "},
                    "steps": [
                        {
                            "label": frame.name,
                            "method": "animate",
                            "args": [
                                [frame.name],
                                {
                                    "mode": "immediate",
                                    "frame": {"duration": 0, "redraw": True},
                                },
                            ],
                        }
                        for frame in frames
                    ],
                }
            ],
        ),
    )
    return figure