import dash_bootstrap_components as dbc
from dash import dcc, html
from plotly.graph_objects import Figure

ANIMATION_TOGGLE_ID = "animation-panel-toggle"
ANIMATION_PANEL_ID = "animation-panel"
ANIMATION_GRAPH_ID = "animation-graph"
ANIMATION_STATUS_ID = "animation-status"


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
                        dcc.Graph(
                            id=ANIMATION_GRAPH_ID,
                            figure=Figure(),
                            style={"width": "100%", "minHeight": "500px"},
                            config={"displaylogo": False},
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