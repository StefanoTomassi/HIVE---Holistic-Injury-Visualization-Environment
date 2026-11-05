"""Dynasaur measurement selection page."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

import dash_bootstrap_components as dbc
from dash import ALL, Dash, Input, Output, ctx, dcc, html, register_page

from core.io.select_folder import choose_files, choose_folder
from whiplash_analysis.whiplash import export_node_kinematics_data


_DICTIONARY_PATH = (
    Path(__file__).resolve().parents[3] / "core" / "dynasaurdata_viz_dictionary.txt"
)


class DynasaurGroup(TypedDict):
    """Metadata and measurements for one Dynasaur output file."""

    description: str
    filename: str
    measurements: Dict[str, str]


def _load_measurements() -> Dict[str, DynasaurGroup]:
    """Load the Dynasaur output groups and measurements from the project dictionary."""
    if not _DICTIONARY_PATH.is_file():
        raise FileNotFoundError(f"Dynasaur dictionary not found: {_DICTIONARY_PATH}")

    dictionary_text = _DICTIONARY_PATH.read_text(encoding="utf-8")
    dictionary_text = re.sub(
        r"\n}\n(?=[A-Za-z0-9_]+\s*:)",
        "\n},\n",
        dictionary_text,
    )
    dictionary_text = re.sub(
        r"^([A-Za-z0-9_]+)\s*:",
        r"'\1':",
        dictionary_text,
        flags=re.MULTILINE,
    )
    parsed_dictionary = ast.literal_eval(f"{{\n{dictionary_text}\n}}")
    measurements: Dict[str, DynasaurGroup] = {}
    for group_name, group in parsed_dictionary.items():
        if not isinstance(group, dict):
            raise ValueError(f"Invalid Dynasaur group '{group_name}'.")
        description = group.get("description")
        filename = group.get("filename")
        channels = group.get("measurements")
        if (
            not isinstance(description, str)
            or not isinstance(filename, str)
            or not isinstance(channels, dict)
            or not all(
                isinstance(channel, str) and isinstance(channel_description, str)
                for channel, channel_description in channels.items()
            )
        ):
            raise ValueError(f"Invalid metadata for Dynasaur group '{group_name}'.")
        measurements[group_name] = {
            "description": description,
            "filename": filename,
            "measurements": channels,
        }

    if not measurements:
        raise ValueError(f"No Dynasaur measurement groups found in {_DICTIONARY_PATH}.")
    return measurements


MEASUREMENTS = _load_measurements()


def register_callbacks(app: Dash) -> None:
    """Register callbacks for exporting selected Dynasaur node measurements."""

    @app.callback(
        Output("dynasaur-request-status", "children"),
        Input("dynasaur-request-data-button", "n_clicks"),
        Input({"type": "dynasaur-measurement-dropdown", "group": ALL}, "value"),
        prevent_initial_call=True,
    )
    def request_data(
        n_clicks: Optional[int],
        selected_values: List[Optional[List[str]]],
    ) -> str:
        """Select source files and export the requested node measurements."""
        if not n_clicks:
            return ""

        selected_groups = {
            item["id"]["group"]: values or []
            for item, values in zip(ctx.inputs_list[1], selected_values)
        }
        unsupported_groups = [
            group_name
            for group_name, values in selected_groups.items()
            if values and group_name != "Nodout"
        ]
        if unsupported_groups:
            return (
                "Currently, node kinematics export supports Nodout only. "
                "Clear selections from: " + ", ".join(unsupported_groups)
            )

        quantities = selected_groups.get("Nodout", [])
        if not quantities:
            return "Select at least one measurement from the Nodout group."

        simulation_files_dir = choose_folder(
            "Select folder containing binout* simulation files"
        )
        if not simulation_files_dir:
            return "Data request cancelled: no simulation folder selected."
        keyword_files = choose_files(
            "Select keyword files containing history nodes",
            filetypes=(("Keyword files", "*.k*"), ("All files", "*.*")),
        )
        if not keyword_files:
            return "Data request cancelled: no keyword files selected."
        output_dir = choose_folder("Select folder for exported Dynasaur data")
        if not output_dir:
            return "Data request cancelled: no output folder selected."

        try:
            output_path = export_node_kinematics_data(
                simulation_files_dir=simulation_files_dir,
                keyword_files=keyword_files,
                output_dir=output_dir,
                quantities=quantities,
            )
        except (OSError, ValueError, RuntimeError) as error:
            return f"Data request failed: {error}"
        simulation_path = Path(simulation_files_dir)
        return (
            f"Data exported successfully to {output_path}. "
            "Dynasaur definitions generated: "
            f"{simulation_path / 'object_definition_whiplash_nodes.def'} and "
            f"{simulation_path / 'criteria_definition_whiplash_nodes.def'}."
        )


def _measurement_group(group_name: str, group: DynasaurGroup) -> dbc.AccordionItem:
    """Render one collapsible output group and its measurement selector."""
    channels = group["measurements"]
    options = [
        {"label": f"{description} ({channel})", "value": channel}
        for channel, description in channels.items()
    ]
    return dbc.AccordionItem(
        dcc.Dropdown(
            id={"type": "dynasaur-measurement-dropdown", "group": group_name},
            options=options,
            multi=True,
            placeholder="Select one or more measurements",
            clearable=True,
        ),
        title=(
            f"{group['description']} "
            f"({group['filename']} - {len(channels)} measurements)"
        ),
    )


def dynasaur_selection() -> html.Div:
    """Render the Dynasaur measurement selection page."""
    return html.Div(
        className="app-div",
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Select Dynasaur measurements"),
                            html.P(
                                "Expand an output group and select the time series "
                                "you want to use.",
                                className="mb-0",
                            ),
                        ],
                    ),
                    html.Img(
                        src="/assets/dynasaur_logo.svg",
                        alt="Dynasaur logo",
                        style={
                            "height": "109px",
                            "maxWidth": "408px",
                            "objectFit": "contain",
                        },
                    ),
                ],
                style={
                    "alignItems": "center",
                    "display": "flex",
                    "gap": "24px",
                    "justifyContent": "flex-start",
                    "marginBottom": "16px",
                },
            ),
            dbc.Accordion(
                [
                    _measurement_group(group_name, group)
                    for group_name, group in MEASUREMENTS.items()
                ],
                start_collapsed=True,
                always_open=True,
                className="mb-3",
            ),
            dbc.Button(
                "Request data",
                id="dynasaur-request-data-button",
                color="primary",
                className="me-2",
            ),
            dcc.Link(
                dbc.Button("Back to data selection", color="secondary"),
                href="/",
                refresh=False,
            ),
            html.Div(id="dynasaur-request-status", className="mt-3"),
        ],
    )


layout = dynasaur_selection()
register_page(__name__, path="/dynasaur-selection", layout=layout)