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
SIGNAL_PLOT_ONE_SELECTION_ID = "signal-plot-one-selection"
SIGNAL_PLOT_TWO_SELECTION_ID = "signal-plot-two-selection"
SIGNAL_GRAPH_ONE_ID = "signal-measurement-graph-one"
SIGNAL_GRAPH_TWO_ID = "signal-measurement-graph-two"


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


def _measurement_trace(
    signal_data: SignalData,
    time_index: int,
    value_index: int,
) -> go.Scatter:
    """Create a line trace for one selected measurement."""
    time_column = signal_data.dataframe.iloc[:, time_index]
    value_column = signal_data.dataframe.iloc[:, value_index]

    time_values = pd.to_numeric(time_column, errors="coerce")
    measurement_values = pd.to_numeric(value_column, errors="coerce")
    valid_values = time_values.notna() & measurement_values.notna()
    metadata = signal_data.metadata[value_index]
    return go.Scatter(
        x=time_values[valid_values],
        y=measurement_values[valid_values],
        mode="lines",
        name=f"{metadata['part']} - {metadata['quantity']}",
    )


def _measurement_figure(
    traces: List[Tuple[SignalData, int, int]],
) -> go.Figure:
    """Create a figure containing one or more selected measurements."""
    figure = go.Figure()
    for signal_data, time_index, value_index in traces:
        figure.add_trace(_measurement_trace(signal_data, time_index, value_index))
        metadata = signal_data.metadata[value_index]
        figure.update_layout(
            xaxis_title=signal_data.metadata[time_index]["variable"],
            yaxis_title=metadata["variable"],
        )
    figure.update_layout(
        title="Selected measurements",
    )
    return figure


def register_signal_callbacks(app: Dash) -> None:
    """Register callbacks driven by all selected CSV paths."""

    def load_measurements(
        csv_paths: Optional[List[str]],
    ) -> Dict[str, Tuple[str, SignalData, int, int]]:
        catalog: Dict[str, Tuple[str, SignalData, int, int]] = {}
        if not csv_paths:
            return catalog
        for file_index, csv_path in enumerate(csv_paths):
            signal_data = read_csv_data(None, csv_path)
            for time_index, value_index in _measurement_pairs(signal_data):
                key = f"{file_index}:{value_index}"
                catalog[key] = (
                    Path(csv_path).name,
                    signal_data,
                    time_index,
                    value_index,
                )
        return catalog

    def measurement_options(
        catalog: Dict[str, Tuple[str, SignalData, int, int]],
        parts: Optional[List[str]],
    ) -> List[dict]:
        options = []
        for key, (file_name, signal_data, _, value_index) in catalog.items():
            metadata = signal_data.metadata[value_index]
            if not parts or metadata["part"] in parts:
                options.append(
                    {
                        "label": (
                            f"{metadata['part']} - {metadata['quantity']} "
                            f"({file_name})"
                        ),
                        "value": key,
                    }
                )
        return options

    def selected_traces(
        catalog: Dict[str, Tuple[str, SignalData, int, int]],
        selected_values: Optional[List[str]],
    ) -> List[Tuple[SignalData, int, int]]:
        return [
            (catalog[key][1], catalog[key][2], catalog[key][3])
            for key in selected_values or []
            if key in catalog
        ]

    @app.callback(
        Output(SIGNAL_PART_ID, "options"),
        Output(SIGNAL_PART_ID, "value"),
        Input("csv-data-selection", "data"),
    )
    def update_parts(
        csv_paths: Optional[List[str]],
    ) -> Tuple[List[dict], List[str]]:
        catalog = load_measurements(csv_paths)
        parts = sorted(
            {
                signal_data.metadata[value_index]["part"]
                for _, signal_data, _, value_index in catalog.values()
            }
        )
        return [{"label": part, "value": part} for part in parts], (
            parts if parts else []
        )

    @app.callback(
        Output(SIGNAL_PLOT_ONE_SELECTION_ID, "options"),
        Output(SIGNAL_PLOT_ONE_SELECTION_ID, "value"),
        Output(SIGNAL_PLOT_TWO_SELECTION_ID, "options"),
        Output(SIGNAL_PLOT_TWO_SELECTION_ID, "value"),
        Input("csv-data-selection", "data"),
        Input(SIGNAL_PART_ID, "value"),
    )
    def update_measurements(
        csv_paths: Optional[List[str]], parts: Optional[List[str]]
    ) -> Tuple[List[dict], List[str], List[dict], List[str]]:
        options = measurement_options(load_measurements(csv_paths), parts)
        first_value = [options[0]["value"]] if options else []
        return options, first_value, options, []

    @app.callback(
        Output(SIGNAL_GRAPH_ONE_ID, "figure"),
        Output(SIGNAL_GRAPH_TWO_ID, "figure"),
        Input("csv-data-selection", "data"),
        Input(SIGNAL_PLOT_ONE_SELECTION_ID, "value"),
        Input(SIGNAL_PLOT_TWO_SELECTION_ID, "value"),
    )
    def update_plots(
        csv_paths: Optional[List[str]],
        plot_one_values: Optional[List[str]],
        plot_two_values: Optional[List[str]],
    ) -> Tuple[go.Figure, go.Figure]:
        catalog = load_measurements(csv_paths)
        return (
            _measurement_figure(selected_traces(catalog, plot_one_values)),
            _measurement_figure(selected_traces(catalog, plot_two_values)),
        )

def plot_measurements() -> html.Div:
    """Render empty dependent dropdowns populated from the selected CSV."""
    return html.Div(
        [
            dcc.Dropdown(
                id=SIGNAL_PART_ID,
                options=[],
                value=[],
                multi=True,
                clearable=True,
                placeholder="Select one or more parts",
            ),
            html.H6("Plot 1 measurements"),
            dcc.Dropdown(
                id=SIGNAL_PLOT_ONE_SELECTION_ID,
                options=[],
                value=[],
                multi=True,
                clearable=True,
                placeholder="Select measurements for plot 1",
            ),
            html.H6("Plot 2 measurements"),
            dcc.Dropdown(
                id=SIGNAL_PLOT_TWO_SELECTION_ID,
                options=[],
                value=[],
                multi=True,
                clearable=True,
                placeholder="Select measurements for plot 2",
            ),
            dcc.Graph(id=SIGNAL_GRAPH_ONE_ID),
            dcc.Graph(id=SIGNAL_GRAPH_TWO_ID),
        ]
    )