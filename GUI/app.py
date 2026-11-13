import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html, no_update
from dash import dcc
from pathlib import Path
from GUI.layout.pages.curtain import (
    animation_curtain,
    register_animation_callbacks,
)
from GUI.theme.hive_theme import get_theme, register_plotly_theme


# Change this value to compare the five proposals from Style instructions.md:
# clinical, engineering_console, safety_assessment, scandinavian_minimal,
# dark_analysis.
ACTIVE_STYLE = "clinical"


def main() -> None:
    """Run the HIVE Dash application using Dash Pages."""
    theme = get_theme(ACTIVE_STYLE)
    register_plotly_theme(theme)
    app = Dash(
        __name__,
        external_stylesheets=[theme.bootstrap_theme],
        assets_folder=str(
            Path(__file__).resolve().parent.parent / "pictures_and_logo"
        ),
        use_pages=True,
        pages_folder="",
        suppress_callback_exceptions=True,
    )
    app.index_string = app.index_string.replace(
        "</head>",
        f"<style>{theme.css}</style></head>",
    )
    app.title = "HIVE Dashboard"
    from GUI.layout.pages import (
        dynasaur_selection,
        generic_dropdown,
        select_data,
        whiplash_page,
    )
    from GUI.layout.pages import restraint_page
    from GUI.layout.Plots.criteria_plots import register_criteria_callbacks
    from GUI.layout.Plots.signal_plots import register_signal_callbacks

    select_data.register_callbacks(app)
    whiplash_page.register_callbacks(app)
    dynasaur_selection.register_callbacks(app)
    register_signal_callbacks(app)
    register_criteria_callbacks(app)
    register_animation_callbacks(app)
    restraint_page.register_callbacks(app)

    @app.callback(
        Output("url", "pathname"),
        Input("url", "pathname"),
        Input("whiplash-navigation-request", "data"),
    )
    def guard_initial_route(
        pathname: str,
        navigation_requested: bool,
    ) -> str:
        """Keep a stale Whiplash URL from bypassing the module-selection page."""
        if navigation_requested and pathname != "/whiplash":
            return "/whiplash"
        if pathname == "/whiplash" and not navigation_requested:
            return "/"
        return no_update

    app.layout = dbc.Container(
        [
            html.Div(
                [
                    html.H1(app.title, className="mb-0"),
                    html.Img(
                        src="/assets/HIVE_logo.svg",
                        alt="HIVE logo",
                        style={
                            "height": "64px",
                            "maxWidth": "220px",
                            "objectFit": "contain",
                        },
                    ),
                ],
                className="hive-app-header",
                style={
                    "alignItems": "center",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "marginBottom": "20px",
                },
            ),
            dcc.Location(id="url", refresh="callback-nav"),
            dcc.Store(id="csv-data-selection", data=[]),
            dcc.Store(id="d3plot-data-selection", data=None),
            dcc.Store(id="whiplash-node-csv-selection", data=None),
            dcc.Store(id="whiplash-criteria-csv-selection", data=None),
            dcc.Store(id="whiplash-part-energy-csv-selection", data=None),
            dcc.Store(id="whiplash-beam-csv-selection", data=None),
            dcc.Store(id="whiplash-navigation-request", data=False),
            dcc.Store(id="restraint-hbm-results", data=None),
            dcc.Loading(
                dash.page_container,
                type="default",
                fullscreen=True,
                color="#0173b2",
            ),
            animation_curtain(),
            restraint_page.progress_overlay(),
        ],
        fluid=True,
    )
    app.run(debug=True)


if __name__ == "__main__":
    main()
