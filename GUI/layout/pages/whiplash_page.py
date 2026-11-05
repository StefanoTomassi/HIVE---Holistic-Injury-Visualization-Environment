"""Whiplash analysis page and callbacks."""

import re
from typing import Dict, List, Optional, Tuple

import plotly.graph_objects as go
import pandas as pd
from dash import Dash, Input, Output, ctx, dcc, html, register_page

from GUI.layout.Plots.signal_plots import (
    SignalData,
    find_measurement_pairs,
    read_csv_data,
)
from GUI.layout.Plots.criteria_plots import (
    Criterion,
    _criteria_figure,
    read_criteria_data,
)
from whiplash_analysis.reference_values import (
    ROM_labels,
    ROMs,
    intervertebral_discs_force_limits,
    sigma_max_muscle,
)
from whiplash_analysis.whiplash import (
    VIVAPLUS_DICTIONARY_PATH,
    main as run_whiplash_analysis,
    read_vivaplus_categories,
)


WHIPLASH_PAGE_PATH = "/whiplash"
WHIPLASH_CSV_STORE_ID = "whiplash-node-csv-selection"
WHIPLASH_CRITERIA_STORE_ID = "whiplash-criteria-csv-selection"
WHIPLASH_PART_ENERGY_STORE_ID = "whiplash-part-energy-csv-selection"
WHIPLASH_LIGAMENT_CATEGORY_ID = "whiplash-ligament-category"
WHIPLASH_SEGMENTAL_PLOTS_ID = "whiplash-segmental-angulation-plots"
WHIPLASH_CRITERIA_SELECTION_ID = "whiplash-criteria-selection"
WHIPLASH_CRITERIA_GRAPH_ID = "whiplash-criteria-graph"
WHIPLASH_LIGAMENT_EXCEEDANCE_GRAPH_ID = "whiplash-ligament-exceedance-graph"
WHIPLASH_CONTACT_SELECTION_ID = "whiplash-contact-selection"
WHIPLASH_CONTACT_CATEGORY_ID = "whiplash-contact-category"
WHIPLASH_CONTACT_GRAPH_ID = "whiplash-contact-graph"
WHIPLASH_PART_ENERGY_GRAPH_ID = "whiplash-part-energy-graph"
WHIPLASH_PART_ENERGY_CATEGORY_ID = "whiplash-part-energy-category"
WHIPLASH_PART_ENERGY_SELECTION_ID = "whiplash-part-energy-selection"
WHIPLASH_EXCEEDANCE_CATEGORY_ID = "whiplash-disc-joint-exceedance-category"
WHIPLASH_EXCEEDANCE_QUANTITY_ID = "whiplash-disc-joint-exceedance-quantity"
WHIPLASH_EXCEEDANCE_GRAPH_ID = "whiplash-disc-joint-exceedance-graph"
WHIPLASH_BEAM_STORE_ID = "whiplash-beam-csv-selection"
WHIPLASH_BEAM_ID = "whiplash-beam-dropdown"
WHIPLASH_BEAM_PLOT_ONE_ID = "whiplash-beam-plot-one-selection"
WHIPLASH_BEAM_PLOT_TWO_ID = "whiplash-beam-plot-two-selection"
WHIPLASH_BEAM_GRAPH_ONE_ID = "whiplash-beam-graph-one"
WHIPLASH_BEAM_GRAPH_TWO_ID = "whiplash-beam-graph-two"
WHIPLASH_MUSCLE_FORCE_GRAPH_ID = "whiplash-muscle-force-graph"
WHIPLASH_MUSCLE_EXCEEDANCE_GRAPH_ID = "whiplash-muscle-exceedance-graph"
WHIPLASH_TRAJECTORIES_BUTTON_ID = "whiplash-trajectories-button"
WHIPLASH_LIGAMENTS_BUTTON_ID = "whiplash-ligaments-button"
WHIPLASH_MUSCLES_BUTTON_ID = "whiplash-muscles-button"
WHIPLASH_DISCS_BUTTON_ID = "whiplash-discs-button"
WHIPLASH_TRAJECTORIES_SECTION_ID = "whiplash-trajectories-section"
WHIPLASH_LIGAMENTS_SECTION_ID = "whiplash-ligaments-section"
WHIPLASH_MUSCLES_SECTION_ID = "whiplash-muscles-section"
WHIPLASH_DISCS_SECTION_ID = "whiplash-discs-section"

LIGAMENT_CATEGORIES = {
    "cranial": "Cranial ligaments (OC-C1 and C1-C2)",
    "CL": "CL",
    "ALL": "ALL",
    "ISL": "ISL",
    "LF": "LF",
    "PLL": "PLL",
}

SECTION_BUTTON_STYLE = {
    "alignItems": "center",
    "display": "inline-flex",
    "gap": "8px",
    "marginBottom": "10px",
    "marginRight": "10px",
}
SECTION_DOT_STYLE = {
    "borderRadius": "50%",
    "display": "inline-block",
    "height": "10px",
    "width": "10px",
}


def contact_category(name: str) -> Optional[str]:
    normalized_name = name.lower()
    if "_disc_" in normalized_name or "intervertebral" in normalized_name:
        return "discs"
    if "_art_cart_" in normalized_name or "articular-process" in normalized_name:
        return "articular"
    return None


def disc_contact_level(name: str) -> Optional[str]:
    match = re.search(
        r"(?:^|[_-])C([2-7])[_-]?(?:INF|SUP)[_-]?DISC(?:$|[_-])",
        name.upper(),
    )
    if not match:
        return None
    return {
        "2": "C2C3",
        "3": "C3C4",
        "4": "C4C5",
        "5": "C5C6",
        "6": "C6C7",
        "7": "C7T1",
    }[match.group(1)]


layout = html.Div(
    [
        html.H2("Whiplash analysis"),
        html.Div(
            "Choose an analysis section to visualize.",
            className="text-muted mb-3",
        ),
        html.Div(
            [
                html.Button(
                    [
                        html.Span(
                            className="whiplash-section-dot",
                            style=dict(SECTION_DOT_STYLE, backgroundColor="#0173b2"),
                        ),
                        "Kinematics analysis",
                    ],
                    id=WHIPLASH_TRAJECTORIES_BUTTON_ID,
                    className="whiplash-section-button",
                    style=SECTION_BUTTON_STYLE,
                    n_clicks=0,
                ),
                html.Button(
                    [
                        html.Span(
                            className="whiplash-section-dot",
                            style=dict(SECTION_DOT_STYLE, backgroundColor="#d55e00"),
                        ),
                        "Ligaments injury analysis",
                    ],
                    id=WHIPLASH_LIGAMENTS_BUTTON_ID,
                    className="whiplash-section-button",
                    style=SECTION_BUTTON_STYLE,
                    n_clicks=0,
                ),
                html.Button(
                    [
                        html.Span(
                            className="whiplash-section-dot",
                            style=dict(SECTION_DOT_STYLE, backgroundColor="#029e73"),
                        ),
                        "Muscle injury analysis",
                    ],
                    id=WHIPLASH_MUSCLES_BUTTON_ID,
                    className="whiplash-section-button",
                    style=SECTION_BUTTON_STYLE,
                    n_clicks=0,
                ),
                html.Button(
                    [
                        html.Span(
                            className="whiplash-section-dot",
                            style=dict(SECTION_DOT_STYLE, backgroundColor="#cc78bc"),
                        ),
                        "Intervertebral discs and joints analysis",
                    ],
                    id=WHIPLASH_DISCS_BUTTON_ID,
                    className="whiplash-section-button",
                    style=SECTION_BUTTON_STYLE,
                    n_clicks=0,
                ),
            ],
            className="whiplash-section-buttons",
        ),
        html.Div(
            [
                html.H3("Segmental angulations"),
                html.Div(id=WHIPLASH_SEGMENTAL_PLOTS_ID),
            ],
            id=WHIPLASH_TRAJECTORIES_SECTION_ID,
        ),
        html.Div(
            [
                html.H3("Ligament strain criteria"),
                dcc.Dropdown(
                    id=WHIPLASH_LIGAMENT_CATEGORY_ID,
                    options=[
                        {"label": label, "value": category}
                        for category, label in LIGAMENT_CATEGORIES.items()
                    ],
                    value=list(LIGAMENT_CATEGORIES),
                    multi=True,
                    clearable=True,
                    placeholder="Select ligament categories",
                ),
                dcc.Dropdown(
                    id=WHIPLASH_CRITERIA_SELECTION_ID,
                    options=[],
                    value=[],
                    multi=True,
                    clearable=True,
                    placeholder="Select ligament strain criteria",
                ),
                dcc.Graph(id=WHIPLASH_CRITERIA_GRAPH_ID, figure=go.Figure()),
                html.H4("Ligaments exceeding the upper limit"),
                dcc.Graph(
                    id=WHIPLASH_LIGAMENT_EXCEEDANCE_GRAPH_ID,
                    figure=go.Figure(),
                ),
            ],
            id=WHIPLASH_LIGAMENTS_SECTION_ID,
            style={"display": "none"},
        ),
        html.Div(
            [
                html.H3("Muscle injury analysis"),
                html.H4("Maximum force by muscle component"),
                dcc.Graph(id=WHIPLASH_MUSCLE_FORCE_GRAPH_ID, figure=go.Figure()),
                html.H4("Muscles exceeding the injury limit"),
                dcc.Graph(
                    id=WHIPLASH_MUSCLE_EXCEEDANCE_GRAPH_ID,
                    figure=go.Figure(),
                ),
            ],
            id=WHIPLASH_MUSCLES_SECTION_ID,
            style={"display": "none"},
        ),
        html.Div(
            [
                html.H3("Intervertebral discs and joints analysis"),
                html.H4("Internal energy by part"),
                dcc.Dropdown(
                    id=WHIPLASH_PART_ENERGY_CATEGORY_ID,
                    options=[
                        {"label": "Intervertebral discs", "value": "discs"},
                        {"label": "Articular processes", "value": "articular"},
                    ],
                    value="discs",
                    clearable=False,
                    placeholder="Select an energy category",
                ),
                dcc.Dropdown(
                    id=WHIPLASH_PART_ENERGY_SELECTION_ID,
                    options=[],
                    value=[],
                    multi=True,
                    clearable=True,
                    placeholder="Select energies",
                ),
                dcc.Graph(id=WHIPLASH_PART_ENERGY_GRAPH_ID, figure=go.Figure()),
                html.H4("Contact resultant force"),
                dcc.Dropdown(
                    id=WHIPLASH_CONTACT_CATEGORY_ID,
                    options=[
                        {"label": "Intervertebral discs", "value": "discs"},
                        {"label": "Articular processes", "value": "articular"},
                    ],
                    value="discs",
                    clearable=False,
                    placeholder="Select a contact category",
                ),
                dcc.Dropdown(
                    id=WHIPLASH_CONTACT_SELECTION_ID,
                    options=[],
                    value=[],
                    multi=True,
                    clearable=True,
                    placeholder="Select contact force criteria",
                ),
                dcc.Graph(id=WHIPLASH_CONTACT_GRAPH_ID, figure=go.Figure()),
                html.H4("Components exceeding reference limits"),
                dcc.Dropdown(
                    id=WHIPLASH_EXCEEDANCE_CATEGORY_ID,
                    options=[
                        {"label": "Intervertebral discs", "value": "discs"},
                        {"label": "Articular processes", "value": "articular"},
                    ],
                    value="discs",
                    clearable=False,
                ),
                dcc.Dropdown(
                    id=WHIPLASH_EXCEEDANCE_QUANTITY_ID,
                    options=[
                        {"label": "Contact force", "value": "force"},
                        {"label": "Absorbed energy", "value": "energy"},
                    ],
                    value="force",
                    clearable=False,
                ),
                dcc.Graph(id=WHIPLASH_EXCEEDANCE_GRAPH_ID, figure=go.Figure()),
            ],
            id=WHIPLASH_DISCS_SECTION_ID,
            style={"display": "none"},
        ),
    ]
)
register_page(__name__, path=WHIPLASH_PAGE_PATH, layout=layout)


def register_callbacks(app: Dash) -> None:
    """Connect the main-page whiplash button to the analysis workflow."""

    @app.callback(
        Output(WHIPLASH_TRAJECTORIES_SECTION_ID, "style"),
        Output(WHIPLASH_LIGAMENTS_SECTION_ID, "style"),
        Output(WHIPLASH_MUSCLES_SECTION_ID, "style"),
        Output(WHIPLASH_DISCS_SECTION_ID, "style"),
        Input(WHIPLASH_TRAJECTORIES_BUTTON_ID, "n_clicks"),
        Input(WHIPLASH_LIGAMENTS_BUTTON_ID, "n_clicks"),
        Input(WHIPLASH_MUSCLES_BUTTON_ID, "n_clicks"),
        Input(WHIPLASH_DISCS_BUTTON_ID, "n_clicks"),
        prevent_initial_call=True,
    )
    def show_analysis_section(
        trajectories_clicks: int,
        ligaments_clicks: int,
        muscles_clicks: int,
        discs_clicks: int,
    ) -> Tuple[dict, dict, dict, dict]:
        del trajectories_clicks, ligaments_clicks, muscles_clicks, discs_clicks
        visible_section = {
            WHIPLASH_TRAJECTORIES_BUTTON_ID: WHIPLASH_TRAJECTORIES_SECTION_ID,
            WHIPLASH_LIGAMENTS_BUTTON_ID: WHIPLASH_LIGAMENTS_SECTION_ID,
            WHIPLASH_MUSCLES_BUTTON_ID: WHIPLASH_MUSCLES_SECTION_ID,
            WHIPLASH_DISCS_BUTTON_ID: WHIPLASH_DISCS_SECTION_ID,
        }.get(ctx.triggered_id, WHIPLASH_TRAJECTORIES_SECTION_ID)
        section_ids = (
            WHIPLASH_TRAJECTORIES_SECTION_ID,
            WHIPLASH_LIGAMENTS_SECTION_ID,
            WHIPLASH_MUSCLES_SECTION_ID,
            WHIPLASH_DISCS_SECTION_ID,
        )
        return tuple(
            {"display": "block"} if section_id == visible_section else {"display": "none"}
            for section_id in section_ids
        )

    @app.callback(
        Output("whiplash-analysis-status", "children"),
        Output(WHIPLASH_CSV_STORE_ID, "data"),
        Output(WHIPLASH_CRITERIA_STORE_ID, "data"),
        Output(WHIPLASH_PART_ENERGY_STORE_ID, "data"),
        Output(WHIPLASH_BEAM_STORE_ID, "data"),
        Output("whiplash-navigation-request", "data"),
        Input("whiplash-analysis-button", "n_clicks"),
    )
    def start_whiplash_analysis(
        n_clicks: Optional[int],
    ) -> Tuple[
        str,
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[str],
        bool,
    ]:
        if not n_clicks:
            return "Analysis not started.", None, None, None, None, False
        try:
            csv_path = run_whiplash_analysis()
        except (
            AttributeError,
            ImportError,
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            return (
                f"Whiplash analysis failed: {error}",
                None,
                None,
                None,
                None,
                False,
            )
        if csv_path is None:
            return "Whiplash analysis cancelled.", None, None, None, None, False
        node_csv_path, criteria_csv_path, part_energy_csv_path, beam_csv_path = csv_path
        return (
            f"Whiplash analysis completed: {node_csv_path}",
            str(node_csv_path),
            str(criteria_csv_path),
            str(part_energy_csv_path),
            str(beam_csv_path),
            True,
        )

    def load_measurements(
        csv_path: Optional[str],
    ) -> Dict[str, Tuple[SignalData, int, int]]:
        if not csv_path:
            return {}
        signal_data = read_csv_data(None, csv_path)
        return {
            f"{time_index}:{value_index}": (
                signal_data,
                time_index,
                value_index,
            )
            for time_index, value_index in find_measurement_pairs(signal_data)
        }

    def segmental_part(
        catalog: Dict[str, Tuple[SignalData, int, int]],
        segment: str,
    ) -> Optional[Tuple[SignalData, int, int]]:
        normalized_segment = re.sub(r"[^a-z0-9]", "", segment.lower())
        segment_pattern = re.compile(
            rf"angulation.*segmental.*{re.escape(normalized_segment)}$",
            re.IGNORECASE,
        )
        for signal_data, time_index, value_index in catalog.values():
            metadata = signal_data.metadata[value_index]
            part = re.sub(r"[^a-z0-9]", "", metadata["part"].lower())
            quantity = metadata["quantity"].strip()
            variable = metadata["variable"].strip()
            if (
                part.startswith("segmental")
                and (
                    segment_pattern.search(quantity) is not None
                    or segment_pattern.search(variable) is not None
                )
            ):
                return signal_data, time_index, value_index
        return None

    def load_criteria(csv_path: Optional[str]) -> List[Criterion]:
        if not csv_path:
            return []
        return read_criteria_data(None, csv_path).criteria

    def ligament_category(name: str) -> Optional[str]:
        if "-OC-C1-" in name or "-C1-C2-" in name:
            return "cranial"
        for category in ("CL", "ALL", "ISL", "LF", "PLL"):
            if f"-{category}-" in name:
                return category
        return None

    def filter_ligament_criteria(
        criteria: List[Criterion],
        categories: Optional[List[str]],
    ) -> List[Criterion]:
        selected_categories = set(categories or [])
        return [
            criterion
            for criterion in criteria
            if ligament_category(criterion.name) in selected_categories
        ]

    def muscle_force_results(signal_data: SignalData) -> pd.DataFrame:
        """Aggregate loaded beam data by muscle component without writing a file."""
        muscle_parts = read_vivaplus_categories(VIVAPLUS_DICTIONARY_PATH)["muscles"]
        component_forces: Dict[str, List[float]] = {}
        component_beams: Dict[str, List[str]] = {}

        for _time_index, value_index in find_measurement_pairs(signal_data):
            beam_name = signal_data.metadata[value_index]["part"].strip().lstrip("-")
            component = beam_name if beam_name in muscle_parts else None
            if component is None and beam_name.startswith("Muscle-"):
                candidate = "NE-" + beam_name
                component = candidate if candidate in muscle_parts else None
            if component is None:
                match = re.search(r"(Muscle-.+)$", beam_name)
                candidate = "NE-" + match.group(1) if match else ""
                component = candidate if candidate in muscle_parts else None
            if component is None:
                continue
            values = pd.to_numeric(
                signal_data.dataframe.iloc[:, value_index],
                errors="coerce",
            ).dropna()
            if values.empty:
                continue
            # The binout value is already the beam force. Do not scale it by
            # the muscle area; area is used only for the injury threshold.
            maximum_binout_force = float(values.abs().max())
            component_forces.setdefault(component, []).append(maximum_binout_force)
            component_beams.setdefault(component, []).append(beam_name)

        rows = []
        for component in sorted(component_forces):
            area = muscle_parts[component].get("area")
            if not isinstance(area, (int, float)) or area <= 0:
                continue
            # sigma_max_muscle is GPa; area is mm², so this is the threshold
            # force in N. Dynasaur axial force is reported in kN.
            injury_limit_force = float(sigma_max_muscle) * 1000.0 * float(area)
            maximum_binout_force = max(component_forces[component]) * 1000.0
            rows.append(
                {
                    "component": component,
                    "beam_elements": "|".join(component_beams[component]),
                    "area_mm2": float(area),
                    "maximum_force_N": maximum_binout_force,
                    "injury_limit_N": injury_limit_force,
                    "exceeds_limit": maximum_binout_force > injury_limit_force,
                }
            )
        return pd.DataFrame(rows)

    @app.callback(
        Output(WHIPLASH_MUSCLE_FORCE_GRAPH_ID, "figure"),
        Output(WHIPLASH_MUSCLE_EXCEEDANCE_GRAPH_ID, "figure"),
        Input(WHIPLASH_BEAM_STORE_ID, "data"),
    )
    def plot_muscle_force_results(
        beam_csv_path: Optional[str],
    ) -> Tuple[go.Figure, go.Figure]:
        empty = go.Figure()
        if not beam_csv_path:
            return empty, empty
        results = muscle_force_results(read_csv_data(None, beam_csv_path))
        if results.empty:
            return empty, empty

        def result_figure(data: pd.DataFrame, title: str) -> go.Figure:
            figure = go.Figure()
            injury_limits = (
                ("minor injury", 0.9, "#b8860b"),
                ("major injury", 2.4, "#cc5500"),
                ("rupture injury", 3.0, "#8b0000"),
            )
            bar_colors = []
            for measured_force, limit in zip(
                data["maximum_force_N"], data["injury_limit_N"]
            ):
                threshold = float(limit)
                force = float(measured_force)
                if force >= threshold * 3.0:
                    bar_colors.append("#8b0000")
                elif force >= threshold * 2.4:
                    bar_colors.append("#cc5500")
                elif force >= threshold * 0.9:
                    bar_colors.append("#b8860b")
                else:
                    bar_colors.append("#0173b2")
            figure.add_bar(
                x=data["maximum_force_N"],
                y=list(range(len(data))),
                name="Maximum force",
                marker_color=bar_colors,
                orientation="h",
                width=0.6,
                showlegend=False,
            )
            for label, multiplier, color in injury_limits:
                figure.add_scatter(
                    x=[None],
                    y=[None],
                    name=label,
                    mode="lines",
                    line={"color": color},
                )
                for position, limit in enumerate(data["injury_limit_N"]):
                    threshold = float(limit) * multiplier
                    figure.add_shape(
                        type="line",
                        x0=threshold,
                        x1=threshold,
                        y0=position - 0.35,
                        y1=position + 0.35,
                        line={"color": color},
                    )
            figure.update_yaxes(
                tickmode="array",
                tickvals=list(range(len(data))),
                ticktext=list(data["component"]),
            )
            figure.update_layout(
                title=title,
                xaxis_title="Force [N]",
                yaxis_title="Muscle component",
                hovermode="y unified",
                height=max(300, len(data) * 60),
                yaxis={
                    "range": [-0.5, len(data) - 0.5],
                    "autorange": "reversed",
                },
                margin={"l": 300},
                legend={"x": 1.02, "xanchor": "left"},
            )
            return figure

        exceeded = results[results["exceeds_limit"]]
        return (
            result_figure(results, "Maximum muscle force and injury limit"),
            result_figure(exceeded, "Muscles exceeding injury limit"),
        )

    def part_energy_figure(
        csv_path: Optional[str],
        selected_values: Optional[List[str]] = None,
    ) -> go.Figure:
        """Plot summed energy for each IVD body and energy for each facet joint."""
        if not csv_path:
            return go.Figure()
        signal_data = read_csv_data(None, csv_path)
        pairs = find_measurement_pairs(signal_data)
        labels: List[str] = []
        values: List[float] = []
        energy_limits: List[Optional[float]] = []
        categories = read_vivaplus_categories(VIVAPLUS_DICTIONARY_PATH)
        facet_parts = categories.get("facet joints", {})
        disc_bodies = categories.get("intervertebral disc bodies", {})
        articular_processes = categories.get("articular processes", {})
        selected_indices = {
            int(value)
            for value in selected_values or []
            if value.isdigit()
        }
        for _, value_index in pairs:
            if selected_values and value_index not in selected_indices:
                continue
            series = pd.to_numeric(
                signal_data.dataframe.iloc[:, value_index],
                errors="coerce",
            ).dropna()
            if series.empty:
                continue
            metadata = signal_data.metadata[value_index]
            label = metadata["part"] or metadata["quantity"]
            part_name = label.replace("Part Energy", "").strip()
            labels.append(part_name)
            values.append(float(series.iloc[-1]))
            part_data = (
                facet_parts.get(part_name)
                or disc_bodies.get(part_name)
                or articular_processes.get(part_name)
            )
            limits = part_data.get("limits") if isinstance(part_data, dict) else None
            energy_limits.append(
                float(limits["energy"])
                if isinstance(limits, dict) and isinstance(limits.get("energy"), (int, float))
                else None
            )
        positions = list(range(len(labels)))
        figure = go.Figure(
            go.Bar(
                x=values,
                y=positions,
                orientation="h",
                width=0.6,
                showlegend=False,
            )
        )
        limit_labels = [
            label for label, limit in zip(labels, energy_limits) if limit is not None
        ]
        if limit_labels:
            figure.add_scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Reference limit",
                line={"color": "red"},
            )
            for position, label, limit in zip(positions, labels, energy_limits):
                if limit is None:
                    continue
                figure.add_shape(
                    type="line",
                    x0=limit,
                    x1=limit,
                    y0=position - 0.35,
                    y1=position + 0.35,
                    line={"color": "red"},
                )
        figure.update_yaxes(
            tickmode="array",
            tickvals=positions,
            ticktext=labels,
        )
        figure.update_layout(
            title="Internal energy at the final time instant",
            xaxis_title="Internal energy [J]",
            yaxis_title="Model part",
            height=max(300, len(labels) * 60),
            yaxis={
                "range": [-0.5, len(labels) - 0.5],
                "autorange": "reversed",
            },
            margin={"l": 300},
            legend={"x": 1.02, "xanchor": "left"},
        )
        return figure

    @app.callback(
        Output(WHIPLASH_PART_ENERGY_SELECTION_ID, "options"),
        Output(WHIPLASH_PART_ENERGY_SELECTION_ID, "value"),
        Input(WHIPLASH_PART_ENERGY_STORE_ID, "data"),
        Input(WHIPLASH_PART_ENERGY_CATEGORY_ID, "value"),
    )
    def update_part_energy_options(
        part_energy_csv_path: Optional[str],
        category: Optional[str],
    ) -> Tuple[List[dict], List[str]]:
        if not part_energy_csv_path:
            return [], []
        signal_data = read_csv_data(None, part_energy_csv_path)
        categories = read_vivaplus_categories(VIVAPLUS_DICTIONARY_PATH)
        category_names = {
            "discs": set(categories.get("intervertebral disc bodies", {})),
            "articular": set(categories.get("articular processes", {})),
        }
        allowed_names = category_names.get(category or "", set())
        options = [
            {
                "label": (
                    signal_data.metadata[value_index]["part"]
                    or signal_data.metadata[value_index]["quantity"]
                )
                .replace("Part Energy", "")
                .strip(),
                "value": str(value_index),
            }
            for _, value_index in find_measurement_pairs(signal_data)
            if (
                signal_data.metadata[value_index]["part"]
                or signal_data.metadata[value_index]["quantity"]
            ).replace("Part Energy", "").strip()
            in allowed_names
        ]
        return options, [option["value"] for option in options]

    @app.callback(
        Output(WHIPLASH_PART_ENERGY_GRAPH_ID, "figure"),
        Input(WHIPLASH_PART_ENERGY_STORE_ID, "data"),
        Input(WHIPLASH_PART_ENERGY_SELECTION_ID, "value"),
    )
    def plot_part_internal_energy(
        part_energy_csv_path: Optional[str],
        selected_values: Optional[List[str]],
    ) -> go.Figure:
        return part_energy_figure(part_energy_csv_path, selected_values)

    def disc_joint_exceedance_figure(
        criteria_csv_path: Optional[str],
        part_energy_csv_path: Optional[str],
        category: Optional[str],
        quantity: Optional[str],
    ) -> go.Figure:
        categories = read_vivaplus_categories(VIVAPLUS_DICTIONARY_PATH)
        if quantity == "force":
            records = []
            facet_limits = next(
                (
                    part_data["limits"]
                    for part_data in categories.get("facet joints", {}).values()
                    if isinstance(part_data, dict)
                    and isinstance(part_data.get("limits"), dict)
                ),
                {},
            )
            for criterion in load_criteria(criteria_csv_path):
                if (
                    criterion.criterion_type.lower() != "contact"
                    or contact_category(criterion.name) != category
                ):
                    continue
                limit = None
                if category == "articular":
                    limit = facet_limits.get("load")
                else:
                    disc_level = disc_contact_level(criterion.name)
                    if disc_level is not None:
                        limit = intervertebral_discs_force_limits[disc_level]
                if isinstance(limit, (int, float)):
                    records.append(
                        (
                            criterion.name,
                            float(criterion.value) * 1000.0,
                            float(limit),
                        )
                    )
            x_title = "Contact resultant force [N]"
        elif quantity == "energy" and part_energy_csv_path:
            allowed_names = {
                "discs": set(categories.get("intervertebral disc bodies", {})),
                "articular": set(categories.get("articular processes", {})),
            }.get(category, set())
            signal_data = read_csv_data(None, part_energy_csv_path)
            records = []
            for _, value_index in find_measurement_pairs(signal_data):
                series = pd.to_numeric(
                    signal_data.dataframe.iloc[:, value_index],
                    errors="coerce",
                ).dropna()
                if series.empty:
                    continue
                metadata = signal_data.metadata[value_index]
                label = metadata["part"] or metadata["quantity"]
                name = label.replace("Part Energy", "").strip()
                if name not in allowed_names:
                    continue
                group_data = (
                    categories.get("intervertebral disc bodies", {}).get(name)
                    if category == "discs"
                    else categories.get("articular processes", {}).get(name)
                )
                limits = group_data.get("limits") if isinstance(group_data, dict) else {}
                limit = limits.get("energy") if isinstance(limits, dict) else None
                if isinstance(limit, (int, float)):
                    records.append((name, float(series.iloc[-1]), float(limit)))
            x_title = "Absorbed internal energy [J]"
        else:
            records = []
            x_title = "Value"

        exceeded = [record for record in records if record[1] > record[2]]
        figure = go.Figure()
        positions = list(range(len(exceeded)))
        if exceeded:
            figure.add_bar(
                x=[record[1] for record in exceeded],
                y=positions,
                orientation="h",
                width=0.6,
                showlegend=False,
            )
            figure.add_scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Reference limit",
                line={"color": "red"},
            )
            for position, (_, _, limit) in enumerate(exceeded):
                figure.add_shape(
                    type="line",
                    x0=limit,
                    x1=limit,
                    y0=position - 0.35,
                    y1=position + 0.35,
                    line={"color": "red"},
                )
        else:
            figure.add_annotation(
                text="No components exceed the selected reference limit",
                showarrow=False,
            )
        figure.update_yaxes(
            tickmode="array",
            tickvals=positions,
            ticktext=[record[0] for record in exceeded],
            autorange="reversed",
        )
        figure.update_layout(
            title="Components exceeding reference limit",
            xaxis_title=x_title,
            yaxis_title="Component",
            height=max(300, len(exceeded) * 60),
            margin={"l": 300},
            legend={"x": 1.02, "xanchor": "left"},
        )
        return figure

    @app.callback(
        Output(WHIPLASH_EXCEEDANCE_GRAPH_ID, "figure"),
        Input(WHIPLASH_CRITERIA_STORE_ID, "data"),
        Input(WHIPLASH_PART_ENERGY_STORE_ID, "data"),
        Input(WHIPLASH_EXCEEDANCE_CATEGORY_ID, "value"),
        Input(WHIPLASH_EXCEEDANCE_QUANTITY_ID, "value"),
    )
    def plot_disc_joint_exceedances(
        criteria_csv_path: Optional[str],
        part_energy_csv_path: Optional[str],
        category: Optional[str],
        quantity: Optional[str],
    ) -> go.Figure:
        return disc_joint_exceedance_figure(
            criteria_csv_path,
            part_energy_csv_path,
            category,
            quantity,
        )

    @app.callback(
        Output(WHIPLASH_CRITERIA_SELECTION_ID, "options"),
        Output(WHIPLASH_CRITERIA_SELECTION_ID, "value"),
        Input(WHIPLASH_CRITERIA_STORE_ID, "data"),
        Input(WHIPLASH_LIGAMENT_CATEGORY_ID, "value"),
    )
    def update_criteria_options(
        criteria_csv_path: Optional[str],
        selected_categories: Optional[List[str]],
    ) -> Tuple[List[dict], List[str]]:
        criteria = filter_ligament_criteria(
            [
                criterion
                for criterion in load_criteria(criteria_csv_path)
                if criterion.criterion_type.lower() == "injury"
            ],
            selected_categories,
        )
        options = [
            {
                "label": f"{criterion.name} ({criterion.dimension})",
                "value": str(index),
            }
            for index, criterion in enumerate(criteria)
        ]
        return options, [option["value"] for option in options]

    @app.callback(
        Output(WHIPLASH_CRITERIA_GRAPH_ID, "figure"),
        Output(WHIPLASH_LIGAMENT_EXCEEDANCE_GRAPH_ID, "figure"),
        Input(WHIPLASH_CRITERIA_STORE_ID, "data"),
        Input(WHIPLASH_CRITERIA_SELECTION_ID, "value"),
        Input(WHIPLASH_LIGAMENT_CATEGORY_ID, "value"),
    )
    def plot_criteria(
        criteria_csv_path: Optional[str],
        selected_values: Optional[List[str]],
        selected_categories: Optional[List[str]],
    ) -> Tuple[go.Figure, go.Figure]:
        criteria = filter_ligament_criteria(
            [
                criterion
                for criterion in load_criteria(criteria_csv_path)
                if criterion.criterion_type.lower() == "injury"
            ],
            selected_categories,
        )
        selected = [
            criteria[int(value)]
            for value in selected_values or []
            if value.isdigit() and int(value) < len(criteria)
        ]
        figure = _criteria_figure(selected)
        if figure.data:
            figure.data[0].showlegend = False
            category_positions = list(range(len(selected)))
            figure.data[0].x = [criterion.value for criterion in selected]
            figure.data[0].y = category_positions
            figure.data[0].orientation = "h"
            figure.data[0].width = 0.6
            figure.update_yaxes(
                tickmode="array",
                tickvals=category_positions,
                ticktext=[criterion.name for criterion in selected],
            )
            figure.update_layout(
                height=max(300, len(selected) * 60),
                yaxis={
                    "range": [-0.5, len(selected) - 0.5],
                    "autorange": "reversed",
                },
                margin={"l": 300},
                legend={"x": 1.02, "xanchor": "left"},
            )
        ligament_parts = read_vivaplus_categories(VIVAPLUS_DICTIONARY_PATH).get(
            "ligaments", {}
        )
        lower_limits = []
        upper_limits = []
        limit_names = []
        limit_positions = []
        exceedance_names = []
        exceedance_values = []
        exceedance_lower_limits = []
        exceedance_limits = []
        exceedance_colors = []
        for criterion in selected:
            displayed_value = criterion.value * 100.0
            part_name = (
                criterion.name[:-len("_stress")]
                if criterion.name.endswith("_stress")
                else criterion.name
            )
            part_data = ligament_parts.get(part_name)
            limits = part_data.get("limits") if isinstance(part_data, dict) else None
            if not isinstance(limits, dict):
                continue
            lower = limits.get("lower")
            upper = limits.get("upper")
            if not isinstance(lower, (int, float)) or not isinstance(
                upper, (int, float)
            ):
                continue
            limit_names.append(criterion.name)
            limit_positions.append(selected.index(criterion))
            lower_limits.append(float(lower))
            upper_limits.append(float(upper))
            if displayed_value > float(lower):
                exceedance_names.append(criterion.name)
                exceedance_values.append(displayed_value)
                exceedance_lower_limits.append(float(lower))
                exceedance_limits.append(float(upper))
                exceedance_colors.append(
                    "#8b0000" if displayed_value > float(upper) else "#b8860b"
                )
        if selected:
            figure.data[0].x = [
                criterion.value * 100.0 for criterion in selected
            ]
        if limit_names:
            figure.add_scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Lower limit",
                line={"color": "red"},
                showlegend=False,
            )
            figure.add_scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Upper limit",
                line={"color": "red"},
                showlegend=False,
            )
            for position, lower, upper in zip(
                limit_positions,
                lower_limits,
                upper_limits,
            ):
                figure.add_shape(
                    type="line",
                    x0=lower,
                    x1=lower,
                    y0=position - 0.35,
                    y1=position + 0.35,
                    line={"color": "red"},
                )
                figure.add_shape(
                    type="line",
                    x0=upper,
                    x1=upper,
                    y0=position - 0.35,
                    y1=position + 0.35,
                    line={"color": "red"},
                )
        exceedance_figure = go.Figure()
        if exceedance_names:
            exceedance_figure.add_bar(
                x=exceedance_values,
                y=list(range(len(exceedance_names))),
                name="Measured strain",
                marker_color=exceedance_colors,
                orientation="h",
                width=0.6,
                showlegend=False,
            )
            exceedance_figure.add_scatter(
                x=[None],
                y=[None],
                mode="markers",
                name="Lower-limit exceedance",
                marker={"color": "#b8860b", "size": 10},
            )
            exceedance_figure.add_scatter(
                x=[None],
                y=[None],
                mode="markers",
                name="Upper-limit exceedance",
                marker={"color": "#8b0000", "size": 10},
            )
            for position, lower, upper in zip(
                range(len(exceedance_names)),
                exceedance_lower_limits,
                exceedance_limits,
            ):
                exceedance_figure.add_shape(
                    type="line",
                    x0=lower,
                    x1=lower,
                    y0=position - 0.35,
                    y1=position + 0.35,
                    line={"color": "#b8860b"},
                )
                exceedance_figure.add_shape(
                    type="line",
                    x0=upper,
                    x1=upper,
                    y0=position - 0.35,
                    y1=position + 0.35,
                    line={"color": "#8b0000"},
                )
            exceedance_figure.update_yaxes(
                tickmode="array",
                tickvals=list(range(len(exceedance_names))),
                ticktext=exceedance_names,
            )
            exceedance_figure.update_layout(
                height=max(300, len(exceedance_names) * 60),
                yaxis={
                    "range": [-0.5, len(exceedance_names) - 0.5],
                    "autorange": "reversed",
                },
                margin={"l": 300},
                legend={"x": 1.02, "xanchor": "left"},
            )
        exceedance_figure.update_layout(
            title="Ligaments exceeding upper strain limit",
            xaxis_title="Strain [%]",
            yaxis_title="Ligament",
            hovermode="y unified",
        )
        figure.update_layout(
            title="Ligament strain criteria",
            xaxis_title="Strain [%]",
            yaxis_title="Ligament",
        )
        return figure, exceedance_figure

    @app.callback(
        Output(WHIPLASH_CONTACT_SELECTION_ID, "options"),
        Output(WHIPLASH_CONTACT_SELECTION_ID, "value"),
        Input(WHIPLASH_CRITERIA_STORE_ID, "data"),
        Input(WHIPLASH_CONTACT_CATEGORY_ID, "value"),
    )
    def update_contact_options(
        criteria_csv_path: Optional[str],
        category: Optional[str],
    ) -> Tuple[List[dict], List[str]]:
        criteria = [
            criterion
            for criterion in load_criteria(criteria_csv_path)
            if criterion.criterion_type.lower() == "contact"
            and contact_category(criterion.name) == category
        ]
        options = [
            {
                "label": criterion.name,
                "value": str(index),
            }
            for index, criterion in enumerate(criteria)
        ]
        return options, [option["value"] for option in options]

    @app.callback(
        Output(WHIPLASH_CONTACT_GRAPH_ID, "figure"),
        Input(WHIPLASH_CRITERIA_STORE_ID, "data"),
        Input(WHIPLASH_CONTACT_CATEGORY_ID, "value"),
        Input(WHIPLASH_CONTACT_SELECTION_ID, "value"),
    )
    def plot_contact_forces(
        criteria_csv_path: Optional[str],
        category: Optional[str],
        selected_values: Optional[List[str]],
    ) -> go.Figure:
        contacts = [
            criterion
            for criterion in load_criteria(criteria_csv_path)
            if criterion.criterion_type.lower() == "contact"
            and contact_category(criterion.name) == category
        ]
        selected = [
            contacts[int(value)]
            for value in selected_values or []
            if value.isdigit() and int(value) < len(contacts)
        ]
        displayed_values = [criterion.value * 1000.0 for criterion in selected]
        figure = _criteria_figure(selected)
        positions = list(range(len(selected)))
        if figure.data:
            figure.data[0].x = displayed_values
            figure.data[0].y = positions
            figure.data[0].orientation = "h"
            figure.data[0].width = 0.6
            figure.data[0].showlegend = False
        categories = read_vivaplus_categories(VIVAPLUS_DICTIONARY_PATH)
        facet_limits = next(
            (
                part_data["limits"]
                for part_data in categories.get("facet joints", {}).values()
                if isinstance(part_data, dict) and isinstance(part_data.get("limits"), dict)
            ),
            {},
        )
        reference_limits = []
        reference_names = []
        reference_positions = []
        disc_levels = tuple(intervertebral_discs_force_limits)
        for criterion in selected:
            name = criterion.name
            limit = None
            if contact_category(name) == "articular":
                limit = facet_limits.get("load")
            elif contact_category(name) == "discs":
                disc_level = disc_contact_level(name)
                if disc_level is not None:
                    limit = intervertebral_discs_force_limits[disc_level]
            if isinstance(limit, (int, float)):
                reference_names.append(criterion.name)
                reference_limits.append(float(limit))
                reference_positions.append(selected.index(criterion))
        if reference_names:
            figure.add_scatter(
                x=[None],
                y=[None],
                mode="lines",
                name="Reference limit",
                line={"color": "red"},
            )
            for position, limit in zip(reference_positions, reference_limits):
                figure.add_shape(
                    type="line",
                    x0=limit,
                    x1=limit,
                    y0=position - 0.35,
                    y1=position + 0.35,
                    line={"color": "red"},
                )
        figure.update_yaxes(
            tickmode="array",
            tickvals=positions,
            ticktext=[criterion.name for criterion in selected],
        )
        figure.update_layout(
            title="Maximum contact resultant force",
            xaxis_title="Resultant force [N]",
            yaxis_title="Contact",
            height=max(300, len(selected) * 60),
            yaxis={
                "range": [-0.5, len(selected) - 0.5],
                "autorange": "reversed",
            },
            margin={"l": 300},
            legend={"x": 1.02, "xanchor": "left"},
        )
        return figure

    @app.callback(
        Output(WHIPLASH_SEGMENTAL_PLOTS_ID, "children"),
        Input(WHIPLASH_CSV_STORE_ID, "data"),
    )
    def plot_segmental_angulations(
        csv_path: Optional[str],
    ) -> List[dcc.Graph]:
        catalog = load_measurements(csv_path)
        plots: List[dcc.Graph] = []
        for segment, (minimum, maximum) in zip(ROM_labels, ROMs[1:]):
            figure = go.Figure()
            segment_data = segmental_part(catalog, segment)
            if segment_data:
                signal_data, time_index, value_index = segment_data
                time_values = pd.to_numeric(
                    signal_data.dataframe.iloc[:, time_index],
                    errors="coerce",
                )
                angle_values = pd.to_numeric(
                    signal_data.dataframe.iloc[:, value_index],
                    errors="coerce",
                ) * (180.0 / 3.141592653589793)
                valid_values = time_values.notna() & angle_values.notna()
                figure.add_scatter(
                    x=time_values[valid_values],
                    y=angle_values[valid_values],
                    mode="lines",
                    name=segment,
                )
            else:
                figure.add_annotation(
                    text="No segmental angulation data found in the CSV",
                    showarrow=False,
                )
            minimum_degrees = float(minimum)
            maximum_degrees = float(maximum)
            figure.add_hline(
                y=maximum_degrees,
                line={"color": "#8b0000"},
                annotation={
                    "text": "Hyperflexion",
                    "font": {"color": "#8b0000", "size": 16},
                },
                annotation_position="top right",
            )
            figure.add_hline(
                y=minimum_degrees,
                line={"color": "#8b0000"},
                annotation={
                    "text": "Hyperextension",
                    "font": {"color": "#8b0000", "size": 16},
                },
                annotation_position="bottom right",
            )
            figure.update_layout(
                title=f"Segmental angulation {segment}",
                xaxis_title="Time",
                yaxis_title="Angle [degrees]",
                hovermode="x unified",
            )
            plots.append(dcc.Graph(figure=figure))
        return plots