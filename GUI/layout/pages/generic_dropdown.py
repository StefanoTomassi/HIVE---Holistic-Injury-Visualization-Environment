from dash import dcc, html, register_page

from GUI.layout.Plots.signal_plots import plot_measurements


def generic_dropdown() -> html.Div:
    """Render the analysis dashboard page."""
    return html.Div(
        className="app-div",
        children=[
            
            html.H2("Select analysis data"),
            render(),
            plot_measurements(),
        ],
    )


def render() -> html.Div:
    """Render the reusable analysis dropdown component."""
    return html.Div(
        className="dropdown-container",
        children=[
            html.H6("Patient"),
            dcc.Dropdown(
                id="generic_dropdown_id",
                options=[
                    {"label": "Dante Alighieri", "value": "1"},
                    {"label": "Thomas Mann", "value": "2"},
                    {"label": "William Shakespeare", "value": "3"},
                ],
                multi=False,
                value=None,
                clearable=False,
            ),
        ],
    )


layout = generic_dropdown()
register_page(__name__, path="/dashboard", layout=layout)
