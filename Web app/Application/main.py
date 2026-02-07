from dash import Dash, html
from dash_bootstrap_components.themes import FLATLY
from Components.layout import create_layout
def main():
    app = Dash(external_stylesheets=[FLATLY])
    app.title = "HIVE Dashboard"
    app.layout = create_layout(app)
    app.run()


if __name__ == "__main__":
    main()