from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html


CSV_SEPARATOR = ";"
METADATA_ROWS = 4
CRITERIA_AREA_ID = "criteria-area-dropdown"
CRITERIA_TYPE_ID = "criteria-type-dropdown"
CRITERIA_SELECTION_ID = "criteria-selection-dropdown"
CRITERIA_GRAPH_ID = "criteria-graph"


@dataclass(frozen=True)
class Criterion:
    """One scalar Dynasaur criterion and its metadata."""

    area: str
    criterion_type: str
    name: str
    dimension: str
    value: float
    file_name: str


@dataclass
class CriteriaData:
    """Criteria metadata and scalar results loaded from one CSV file."""

    criteria: List[Criterion]


def read_criteria_data(
    app: Optional[object],
    csv_file_path: str,
    *,
    separator: str = CSV_SEPARATOR,
) -> CriteriaData:
    """Read a Dynasaur criteria CSV with four metadata rows.

    Criteria output contains one result row. Columns with an empty result are
    omitted because no scalar value was computed for that criterion.
    ``app`` is retained for compatibility with the signal reader API.
    """
    del app
    path = Path(csv_file_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Criteria CSV file not found: {path}")

    metadata = pd.read_csv(
        path,
        sep=separator,
        header=None,
        nrows=METADATA_ROWS,
        dtype=str,
    ).fillna("")
    values = pd.read_csv(
        path,
        sep=separator,
        skiprows=METADATA_ROWS,
        header=None,
    )
    if values.shape[0] != 1:
        return CriteriaData(criteria=[])

    criteria: List[Criterion] = []
    for column_index in range(metadata.shape[1]):
        result = pd.to_numeric(values.iloc[0, column_index], errors="coerce")
        name = str(metadata.iloc[2, column_index]).strip()
        if pd.isna(result) or not name:
            continue
        criteria.append(
            Criterion(
                area=str(metadata.iloc[0, column_index]).strip(),
                criterion_type=str(metadata.iloc[1, column_index]).strip(),
                name=name,
                dimension=str(metadata.iloc[3, column_index]).strip(),
                value=float(result),
                file_name=path.name,
            )
        )
    return CriteriaData(criteria=criteria)


def _load_criteria(
    csv_paths: Optional[List[str]],
) -> Dict[str, Criterion]:
    """Load computed criteria from all selected CSV files."""
    catalog: Dict[str, Criterion] = {}
    for file_index, csv_path in enumerate(csv_paths or []):
        data = read_criteria_data(None, csv_path)
        for criterion_index, criterion in enumerate(data.criteria):
            catalog[f"{file_index}:{criterion_index}"] = criterion
    return catalog


def _criteria_figure(criteria: List[Criterion]) -> go.Figure:
    """Create a bar chart for the selected scalar criteria."""
    figure = go.Figure()
    if criteria:
        figure.add_trace(
            go.Bar(
                x=[criterion.name for criterion in criteria],
                y=[criterion.value for criterion in criteria],
                customdata=[
                    [criterion.area, criterion.criterion_type, criterion.dimension]
                    for criterion in criteria
                ],
                hovertemplate=(
                    "%{x}<br>Value: %{y}<br>"
                    "Area: %{customdata[0]}<br>"
                    "Type: %{customdata[1]}<br>"
                    "Dimension: %{customdata[2]}<extra></extra>"
                ),
            )
        )
    figure.update_layout(
        title="Selected injury criteria",
        xaxis_title="Criterion",
        yaxis_title="Value",
    )
    return figure


def register_criteria_callbacks(app: Dash) -> None:
    """Register criteria filters and scalar-result plotting callbacks."""

    @app.callback(
        Output(CRITERIA_AREA_ID, "options"),
        Output(CRITERIA_AREA_ID, "value"),
        Output(CRITERIA_TYPE_ID, "options"),
        Output(CRITERIA_TYPE_ID, "value"),
        Input("csv-data-selection", "data"),
    )
    def update_criteria_filters(
        csv_paths: Optional[List[str]],
    ) -> Tuple[List[dict], List[str], List[dict], List[str]]:
        criteria = list(_load_criteria(csv_paths).values())
        areas = sorted({criterion.area for criterion in criteria})
        types = sorted({criterion.criterion_type for criterion in criteria})
        return (
            [{"label": area, "value": area} for area in areas],
            areas,
            [{"label": criterion_type, "value": criterion_type} for criterion_type in types],
            types,
        )

    @app.callback(
        Output(CRITERIA_SELECTION_ID, "options"),
        Output(CRITERIA_SELECTION_ID, "value"),
        Input("csv-data-selection", "data"),
        Input(CRITERIA_AREA_ID, "value"),
        Input(CRITERIA_TYPE_ID, "value"),
    )
    def update_criteria_options(
        csv_paths: Optional[List[str]],
        areas: Optional[List[str]],
        criterion_types: Optional[List[str]],
    ) -> Tuple[List[dict], List[str]]:
        criteria = _load_criteria(csv_paths)
        filtered = [
            (key, criterion)
            for key, criterion in criteria.items()
            if (not areas or criterion.area in areas)
            and (not criterion_types or criterion.criterion_type in criterion_types)
        ]
        options = [
            {
                "label": f"{criterion.name} ({criterion.file_name})",
                "value": key,
            }
            for key, criterion in filtered
        ]
        return options, [option["value"] for option in options]

    @app.callback(
        Output(CRITERIA_GRAPH_ID, "figure"),
        Input("csv-data-selection", "data"),
        Input(CRITERIA_SELECTION_ID, "value"),
    )
    def update_criteria_graph(
        csv_paths: Optional[List[str]],
        selected_values: Optional[List[str]],
    ) -> go.Figure:
        catalog = _load_criteria(csv_paths)
        selected = [
            catalog[key] for key in selected_values or [] if key in catalog
        ]
        return _criteria_figure(selected)


def plot_criteria() -> html.Div:
    """Render criteria filters and the scalar-result chart."""
    return html.Div(
        [
            html.H3("Injury criteria"),
            dcc.Dropdown(
                id=CRITERIA_AREA_ID,
                options=[],
                value=[],
                multi=True,
                clearable=True,
                placeholder="Select body area",
            ),
            dcc.Dropdown(
                id=CRITERIA_TYPE_ID,
                options=[],
                value=[],
                multi=True,
                clearable=True,
                placeholder="Select criterion type",
            ),
            dcc.Dropdown(
                id=CRITERIA_SELECTION_ID,
                options=[],
                value=[],
                multi=True,
                clearable=True,
                placeholder="Select computed criteria",
            ),
            dcc.Graph(id=CRITERIA_GRAPH_ID),
        ]
    )