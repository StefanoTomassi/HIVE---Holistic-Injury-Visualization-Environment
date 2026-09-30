import base64
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import dash_bootstrap_components as dbc
import numpy as np
from dash import Dash, Input, Output, State, dcc, html

from core.io.find_simulation_files import find_output_simulation_files

ANIMATION_TOGGLE_ID = "animation-panel-toggle"
ANIMATION_PANEL_ID = "animation-panel"
ANIMATION_IMAGE_ID = "animation-image"
ANIMATION_STATUS_ID = "animation-status"


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


def _create_animation_gif(folder: str, state_stride: int = 2) -> str:
    """Create a lightweight PyVista point animation and return a data URI."""
    import lsreader as lr
    import pyvista as pv

    _, d3plots = find_output_simulation_files(folder)
    if not d3plots:
        raise FileNotFoundError(f"No d3plot files found in {folder}")
    d3plot_path = d3plots[0]
    reader = lr.D3plotReader(d3plot_path)
    try:
        num_states = int(reader.get_data(lr.DataType.D3P_NUM_STATES))
    finally:
        reader.close()
    if num_states < 1:
        raise ValueError("The d3plot file contains no animation states.")

    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as handle:
        gif_path = Path(handle.name)
    plotter = pv.Plotter(off_screen=True, window_size=(900, 600))
    try:
        mesh = pv.PolyData(_read_coordinates(d3plot_path, 0))
        plotter.set_background("white")
        plotter.add_points(mesh, color="#0173b2", point_size=3)
        plotter.camera_position = "xy"
        plotter.open_gif(str(gif_path), fps=12)
        for timestep in range(0, num_states, max(1, state_stride)):
            mesh.points = _read_coordinates(d3plot_path, timestep)
            plotter.write_frame()
        plotter.close()
    finally:
        if gif_path.exists():
            encoded = base64.b64encode(gif_path.read_bytes()).decode("ascii")
            gif_path.unlink()
        else:
            encoded = ""
    if not encoded:
        raise RuntimeError("PyVista did not produce an animation frame.")
    return f"data:image/gif;base64,{encoded}"


def animation_curtain() -> html.Div:
    """Render the animation drawer and its compact side handle."""
    return html.Div(
        [
            dbc.Button(
                "Animation >",
                id=ANIMATION_TOGGLE_ID,
                n_clicks=0,
                className=(
                    "position-fixed top-50 end-0 translate-middle-y "
                    "d-flex align-items-center"
                ),
                title="Open simulation animation",
                style={
                    "backgroundColor": "#029e73",
                    "borderRadius": "8px 0 0 8px",
                    "border": "none",
                    "color": "white",
                    "fontWeight": "bold",
                    "padding": "14px 8px",
                    "writingMode": "vertical-rl",
                    "zIndex": 2000,
                },
            ),
            dbc.Offcanvas(
                [
                    html.Div(
                        "Select a d3plot folder to load the animation.",
                        id=ANIMATION_STATUS_ID,
                        className="text-muted mb-2",
                    ),
                    dcc.Loading(
                        html.Img(
                            id=ANIMATION_IMAGE_ID,
                            style={"width": "100%", "minHeight": "240px"},
                        )
                    ),
                ],
                id=ANIMATION_PANEL_ID,
                title="Simulation animation",
                placement="end",
                is_open=False,
                scrollable=True,
                backdrop=False,
                style={"width": "50vw", "minWidth": "420px"},
            ),
        ]
    )


def register_animation_callbacks(app: Dash) -> None:
    """Connect the drawer, folder selection, and animation rendering."""

    @app.callback(
        Output(ANIMATION_PANEL_ID, "is_open"),
        Input(ANIMATION_TOGGLE_ID, "n_clicks"),
        State(ANIMATION_PANEL_ID, "is_open"),
        prevent_initial_call=True,
    )
    def toggle_animation_panel(n_clicks: int, is_open: bool) -> bool:
        del n_clicks
        return not is_open

    @app.callback(
        Output(ANIMATION_TOGGLE_ID, "children"),
        Input(ANIMATION_PANEL_ID, "is_open"),
    )
    def update_animation_handle(is_open: bool) -> str:
        return "Animation <" if is_open else "Animation >"

    @app.callback(
        Output(ANIMATION_IMAGE_ID, "src"),
        Output(ANIMATION_STATUS_ID, "children"),
        Input("d3plot-data-selection", "data"),
        prevent_initial_call=True,
    )
    def load_animation(
        d3plot_folder: Optional[str],
    ) -> Tuple[Optional[str], str]:
        if not d3plot_folder:
            return None, "Select a d3plot folder to load the animation."
        try:
            image = _create_animation_gif(d3plot_folder)
        except (
            FileNotFoundError,
            ImportError,
            OSError,
            ValueError,
            RuntimeError,
        ) as error:
            return None, f"Animation could not be loaded: {error}"
        return image, "Animation loaded from the selected d3plot folder."
