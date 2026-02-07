from dash import Dash, html, dcc
from dash.dependencies import Input, Output
def render(app:_Dash) -> html.Div:
    return html.Div(
        #callback example for dropdown,
        
            
        children=[
            html.H6("Patient"),
            dcc.Dropdown(
                id = "generic_dropdown_id",
                options=[
                    {"label": "Dante Alighieri", "value": "1"},
                    {"label": "Thomas Mann", "value": "2"},
                    {"label": "William Shakespeare", "value": "3"},
                ],
                multi=False,
                value= [],
                clearable=False,
            )
        ]
    )