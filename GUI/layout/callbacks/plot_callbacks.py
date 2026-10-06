from pathlib import Path
from typing import Optional, Tuple

from dash import Dash, Input, Output, State
from plotly.graph_objects import Figure

from GUI.layout.viewer.pyvista_adapter import _create_animation_figure
from GUI.layout.viewer.viewer_3d import (
    ANIMATION_GRAPH_ID,
    ANIMATION_PANEL_ID,
    ANIMATION_STATUS_ID,
    ANIMATION_TOGGLE_ID,
)


def register_animation_callbacks(app: Dash) -> None:
    """Connect the animation drawer, folder selection, and rendering."""

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
        Output(ANIMATION_GRAPH_ID, "figure"),
        Output(ANIMATION_STATUS_ID, "children"),
        Input("d3plot-data-selection", "data"),
        prevent_initial_call=True,
    )
    def load_animation(
        d3plot_folder: Optional[str],
    ) -> Tuple[Optional[Figure], str]:
        if not d3plot_folder:
            return Figure(), "Select a d3plot folder to load the animation."
        connectivity_path = Path(d3plot_folder) / "element_connectivity.pkl"
        try:
            figure = _create_animation_figure(
                d3plot_folder,
                str(connectivity_path),
            )
        except (
            AttributeError,
            FileNotFoundError,
            IndexError,
            ImportError,
            OSError,
            TypeError,
            ValueError,
            RuntimeError,
        ) as error:
            return (
                Figure(),
                f"Animation could not be loaded ({type(error).__name__}): {error}",
            )
        return figure, "Interactive mesh animation loaded from the selected d3plot folder."
