from pathlib import Path
from typing import List, Optional, Tuple

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, ctx, dcc, html, register_page
from dash.exceptions import PreventUpdate

from core.io.select_folder import choose_files, choose_folder


def register_callbacks(app: Dash) -> None:
    """Register callbacks used by the simulation-data page."""

    @app.callback(
        Output("csv-data-selection", "data"),
        Output("csv-data-selection-label", "children"),
        Output("d3plot-data-selection", "data"),
        Output("d3plot-data-selection-label", "children"),
        Input("csv-data-file-button", "n_clicks"),
        Input("d3plot-data-file-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def select_data(
        csv_clicks: Optional[int],
        d3plot_clicks: Optional[int],
    ) -> Tuple[List[str], str, Optional[str], str]:
        """Open the appropriate native selector for the clicked card."""
        if ctx.triggered_id == "csv-data-file-button":
            if not csv_clicks or csv_clicks < 1:
                raise PreventUpdate
            selected_files = choose_files(
                "Select CSV data files",
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            )
            paths = [str(Path(path).resolve()) for path in selected_files]
            label = (
                f"{len(paths)} CSV file(s) selected:\n {', '.join(paths)}"
                if paths
                else "No CSV files selected."
            )
            return paths, label, None, "No d3plot folder selected."

        if ctx.triggered_id == "d3plot-data-file-button":
            if not d3plot_clicks or d3plot_clicks < 1:
                raise PreventUpdate
            selected_folder = choose_folder("Select the folder containing d3plot")
            folder = str(Path(selected_folder).resolve()) if selected_folder else None
            label = (
                f"Selected d3plot folder: {folder}"
                if folder
                else "No d3plot folder selected."
            )
            return [], "No CSV files selected.", folder, label
        raise PreventUpdate

def select_simulation_data() -> html.Div:
    """Render the simulation-data selection page."""
    return html.Div(
        children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(
                            "Select already processed csv datafiles",
                            className="card-title",
                        ),
                        html.P(
                            "Choose the simulation data you want to visualize.",
                            className="card-text",
                        ),
                        dbc.Button(
                            "Select Data",
                            color="primary",
                            id="csv-data-file-button",
                        ),
                        html.Div(
                            "No CSV files selected.",
                            id="csv-data-selection-label",
                            className="mt-2",
                        ),
                    ]
                )
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4(
                            "Select folder with d3plot datafiles",
                            className="card-title",
                        ),
                        html.P(
                            "Choose the simulation data you want to visualize.",
                            className="card-text",
                        ),
                        dbc.Button(
                            "Select Data",
                            color="primary",
                            id="d3plot-data-file-button",
                        ),
                        html.Div(
                            "No d3plot folder selected.",
                            id="d3plot-data-selection-label",
                            className="mt-2",
                        ),
                    ]
                )
            ),
            dcc.Link(
                dbc.Button("Run analysis", color="primary", className="mt-3"),
                href="/dashboard",
                id="run-analysis-link",
                refresh=False,
                ),
        ]
    )


layout = select_simulation_data()
register_page(__name__, path="/", layout=layout)
