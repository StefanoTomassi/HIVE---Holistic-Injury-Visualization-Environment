import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
from dash import dcc
from GUI.layout.pages.animation_curtain import (
    animation_curtain,
    register_animation_callbacks,
)


def main() -> None:
    """Run the HIVE Dash application using Dash Pages."""
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.MINTY],
        use_pages=True,
        pages_folder="",
    )
    app.title = "HIVE Dashboard"
    from GUI.layout.pages import generic_dropdown, select_data
    from GUI.layout.Plots.criteria_plots import register_criteria_callbacks
    from GUI.layout.Plots.signal_plots import register_signal_callbacks

    select_data.register_callbacks(app)
    register_signal_callbacks(app)
    register_criteria_callbacks(app)
    register_animation_callbacks(app)

    app.layout = dbc.Container(
        [
            html.H1(app.title),
            dcc.Store(id="csv-data-selection", data=[]),
            dcc.Store(id="d3plot-data-selection", data=None),
            dash.page_container,
            animation_curtain(),
        ],
        fluid=True,
    )
    app.run(debug=True)


if __name__ == "__main__":
    main()
