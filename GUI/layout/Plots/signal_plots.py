from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html


CSV_SEPARATOR = ";"
METADATA_ROWS = 4
SIGNAL_PART_ID = "signal-part-dropdown"
SIGNAL_MEASUREMENT_ID = "signal-measurement-dropdown"
SIGNAL_GRAPH_ID = "signal-measurement-graph"


@dataclass
class SignalData:
    """A long-format signal dataframe and its column metadata."""

    dataframe: pd.DataFrame
    metadata: List[Dict[str, str]]


def read_csv_data(
    app: Optional[object],
    csv_file_path: str,
    *,
    separator: str = CSV_SEPARATOR,
) -> SignalData:
    """Load a Dynasaur CSV and preserve its four metadata rows.

    The first four rows describe each column as anatomical part, quantity,
    variable/label, and unit. The remaining rows are loaded as the dataframe.
    ``app`` is retained for compatibility with existing Dash callers.
    """
    del app
    path = Path(csv_file_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    header = pd.read_csv(
        path,
        sep=separator,
        header=None,
        nrows=METADATA_ROWS,
        dtype=str,
    ).fillna("")
    metadata = []
    for column_index in range(header.shape[1]):
        values = [
            str(header.iloc[row_index, column_index]).strip()
            for row_index in range(METADATA_ROWS)
        ]
        part = values[0]
        raw_quantity = values[1]
        raw_variable = values[2]
        quantity_prefix = f"{part}_"
        quantity = (
            raw_quantity[len(quantity_prefix):]
            if raw_quantity.startswith(quantity_prefix)
            else raw_quantity
        ).replace("_", " ")
        unit_match = re.search(r"\[([^\]]*)\]", raw_variable)
        unit = unit_match.group(1).strip() if unit_match else ""
        variable = re.sub(r"\s*\[[^\]]*\]", "", raw_variable).strip()
        variable = variable.replace("_", " ")
        metadata.append(
            {
                "part": part,
                "quantity": quantity,
                "variable": variable,
                "unit": unit,
            }
        )

    dataframe = pd.read_csv(
        path,
        sep=separator,
        skiprows=METADATA_ROWS,
        header=None,
    )
    dataframe.columns = [f"column_{index}" for index in range(dataframe.shape[1])]
    return SignalData(dataframe=dataframe, metadata=metadata)


def _measurement_pairs(signal_data: SignalData) -> List[Tuple[int, int]]:
    """Return time/value column pairs from the signal metadata."""
    pairs = [
        (index, index + 1)
        for index, metadata in enumerate(signal_data.metadata[:-1])
        if metadata["variable"].lower() == "time"
    ]
    if not pairs:
        raise ValueError("The CSV does not contain a time/value measurement pair.")
    return pairs


def _measurement_figure(
    signal_data: SignalData,
    time_index: int,
    value_index: int,
) -> go.Figure:
    """Create a line figure for one selected measurement."""
    time_column = signal_data.dataframe.iloc[:, time_index]
    value_column = signal_data.dataframe.iloc[:, value_index]

    time_values = pd.to_numeric(time_column, errors="coerce")
    measurement_values = pd.to_numeric(value_column, errors="coerce")
    valid_values = time_values.notna() & measurement_values.notna()
    metadata = signal_data.metadata[value_index]
    figure = go.Figure(
        data=[
            go.Scatter(
                x=time_values[valid_values],
                y=measurement_values[valid_values],
                mode="lines",
                name=metadata["quantity"],
            )
        ]
    )
    figure.update_layout(
        title=f"{metadata['part']} - {metadata['quantity']}",
        xaxis_title=signal_data.metadata[time_index]["variable"],
        yaxis_title=metadata["variable"],
    )
    return figure


def register_signal_callbacks(app: Dash) -> None:
    """Register callbacks driven by the selected CSV path."""

    def load_measurements(csv_paths: Optional[List[str]]) -> Tuple[
        Optional[SignalData], Dict[str, List[Tuple[str, int, int]]]
    ]:
        if not csv_paths:
            return None, {}
        signal_data = read_csv_data(None, csv_paths[0])
        measurements_by_part: Dict[str, List[Tuple[str, int, int]]] = {}
        for time_index, value_index in _measurement_pairs(signal_data):
            metadata = signal_data.metadata[value_index]
            measurements_by_part.setdefault(metadata["part"], []).append(
                (metadata["quantity"], time_index, value_index)
            )
        return signal_data, measurements_by_part

    @app.callback(
        Output(SIGNAL_PART_ID, "options"),
        Output(SIGNAL_PART_ID, "value"),
        Input("csv-data-selection", "data"),
    )
    def update_parts(
        csv_paths: Optional[List[str]],
    ) -> Tuple[List[dict], Optional[str]]:
        _, measurements_by_part = load_measurements(csv_paths)
        parts = sorted(measurements_by_part)
        return (
            [{"label": part, "value": part} for part in parts],
            parts[0] if parts else None,
        )

    @app.callback(
        Output(SIGNAL_MEASUREMENT_ID, "options"),
        Output(SIGNAL_MEASUREMENT_ID, "value"),
        Input("csv-data-selection", "data"),
        Input(SIGNAL_PART_ID, "value"),
    )
    def update_measurements(
        csv_paths: Optional[List[str]], part: Optional[str]
    ) -> Tuple[List[dict], Optional[str]]:
        _, measurements_by_part = load_measurements(csv_paths)
        options = [
            {"label": quantity, "value": str(value_index)}
            for quantity, _, value_index in measurements_by_part.get(part or "", [])
        ]
        return options, options[0]["value"] if options else None

    @app.callback(
        Output(SIGNAL_GRAPH_ID, "figure"),
        Input("csv-data-selection", "data"),
        Input(SIGNAL_PART_ID, "value"),
        Input(SIGNAL_MEASUREMENT_ID, "value"),
    )
    def update_plot(
        csv_paths: Optional[List[str]],
        part: Optional[str],
        value_index: Optional[str],
    ) -> go.Figure:
        signal_data, measurements_by_part = load_measurements(csv_paths)
        if signal_data is None:
            return go.Figure()
        entries = measurements_by_part.get(part or "", [])
        selected = next(
            (entry for entry in entries if str(entry[2]) == value_index),
            None,
        )
        if selected is None:
            return go.Figure()
        _, time_index, selected_value_index = selected
        return _measurement_figure(signal_data, time_index, selected_value_index)

def plot_random_measurement() -> html.Div:
    """Render empty dependent dropdowns populated from the selected CSV."""
    return html.Div(
        [
            dcc.Dropdown(
                id=SIGNAL_PART_ID,
                options=[],
                value=None,
                clearable=False,
            ),
            dcc.Dropdown(
                id=SIGNAL_MEASUREMENT_ID,
                options=[],
                value=None,
                clearable=False,
            ),
            dcc.Graph(id=SIGNAL_GRAPH_ID),
        ]
    )