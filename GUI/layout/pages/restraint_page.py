"""Restraint-system analysis page (v1: VIVA+ HBM injury criteria).

Written for two audiences:

* everyone - a plain-language summary with traffic-light risk cards, an
  "injury risk by severity (AIS)" chart and an occupant-motion animation;
* engineers - per-region time histories, limits with sources and a table
  of every computed value.
"""

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update, register_page
from dash.exceptions import PreventUpdate
from plotly.colors import sample_colorscale

from restraint_system_analysis.hbm import METADATA_ROWS, read_dynasaur_csv
from restraint_system_analysis.hbm_criteria import (
    HEAD,
    LOWER,
    MOTION,
    NECK,
    THORAX,
    VEHICLE_REFERENCE,
)
from restraint_system_analysis.hbm_model import load_hbm_dictionary
from GUI.layout.pages import restraint_style as style
from GUI.layout.pages.whiplash_page import SECTION_BUTTON_STYLE, SECTION_DOT_STYLE
from restraint_system_analysis.reference_values import (
    AIS_DESCRIPTIONS,
    BRIC_LIMITS,
    CHEST_DEFLECTION_LIMITS,
    HIC15_LIMITS,
    HIC_RISK_LOGNORMAL,
    NIC_LIMITS,
    RIB_RISK_AGES,
    SOURCES,
    Limit,
    hic_risk,
)

RESTRAINT_PAGE_PATH = "/restraint"
RESTRAINT_RESULTS_STORE_ID = "restraint-hbm-results"
RESTRAINT_BUTTON_ID = "restraint-system-analysis-button"
RESTRAINT_STATUS_ID = "restraint-analysis-status"
RESTRAINT_RIB_AGE_ID = "restraint-rib-age"
SECTION_IDS = {
    "overview": "restraint-overview-section",
    MOTION: "restraint-motion-section",
    HEAD: "restraint-head-section",
    NECK: "restraint-neck-section",
    THORAX: "restraint-thorax-section",
    LOWER: "restraint-lower-section",
    "details": "restraint-details-section",
}
SECTION_LABELS = {
    "overview": "Summary",
    MOTION: "Occupant motion",
    HEAD: "Head",
    NECK: "Neck",
    THORAX: "Chest",
    LOWER: "Lower body",
    "details": "Engineering details",
}
LIMIT_COLORS = style.LIMIT_COLORS
AIS_COLORS = style.AIS_COLORS
#: Traffic light: (upper bound of probability, label, bootstrap colour).
RISK_BANDS = ((0.10, "Low", "success"), (0.50, "Medium", "warning"),
              (1.01, "High", "danger"))
G = 9.80665
INDICATIVE_NOTE = (
    "Regulatory and Euro NCAP limits are Hybrid III 50M (crash-test dummy) limits "
    "and are shown for the human body model as indicative values only. VIVA+ risk "
    "functions are the primary HBM measure where available."
)
GRAPH_LAYOUT = dict(
    legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="left", x=0),
    margin=dict(l=60, r=20, t=50, b=60),
)

PROGRESS_OVERLAY_ID = "restraint-progress-overlay"
_OVERLAY_HIDDEN = {"display": "none"}
_OVERLAY_SHOWN = {
    "alignItems": "center", "backgroundColor": style.OVERLAY_BACKDROP,
    "display": "flex", "inset": "0", "justifyContent": "center",
    "position": "fixed", "zIndex": 2000,
}


def progress_overlay() -> html.Div:
    """Full-screen progress card shown while the analysis runs (any page)."""
    return html.Div([
        dcc.Interval(id="restraint-progress-interval", interval=800),
        html.Div(dbc.Card(dbc.CardBody([
            html.H4("Restraint system analysis running", className="mb-3"),
            dbc.Progress(id="restraint-progress-bar", value=0, striped=True,
                         animated=True, style={"height": "22px"}, className="mb-3"),
            html.Div(id="restraint-progress-message", className="mb-1"),
            html.Div(id="restraint-progress-elapsed", className="text-muted small"),
            html.Div("Detailed output is printed in the terminal.",
                     className="text-muted small"),
        ]), style={"maxWidth": "560px", "width": "90%"}),
            id=PROGRESS_OVERLAY_ID, style=_OVERLAY_HIDDEN),
    ])


# --- Layout helpers -----------------------------------------------------------
def _button(key: str) -> html.Button:
    """Section button, same look as the whiplash page."""
    color = style.SECTION_COLORS[key.lower()]
    return html.Button(
        [html.Span(className="whiplash-section-dot",
                   style=dict(SECTION_DOT_STYLE, backgroundColor=color)),
         SECTION_LABELS[key]],
        id=f"restraint-{key.lower()}-button",
        className="whiplash-section-button",
        n_clicks=0,
        style=SECTION_BUTTON_STYLE,
    )


def _graph(graph_id: str, caption: str = "") -> html.Div:
    children = [dcc.Graph(id=graph_id, figure=go.Figure(),
                          config=style.graph_config(graph_id.replace("restraint-", "hive_")))]
    if caption:
        children.append(html.P(caption, className="text-muted small mb-4"))
    return html.Div(children)


def _plain(text: str) -> dbc.Alert:
    """A short 'in plain words' explanation box."""
    return dbc.Alert([html.B("In plain words: "), text], color="light",
                     className="border")


def _ais_explainer() -> dbc.Accordion:
    rows = [html.Tr([html.Td(f"AIS {level}"), html.Td(name), html.Td(example)])
            for level, (name, example) in AIS_DESCRIPTIONS.items()]
    return dbc.Accordion([dbc.AccordionItem([
        html.P("Doctors grade injuries on the Abbreviated Injury Scale (AIS) from 1 "
               "(minor) to 6 (maximal). 'AIS 3+' means an injury of grade 3 or worse. "
               "The percentages on this page are the estimated chance that such an "
               "injury happens in this crash."),
        dbc.Table([html.Thead(html.Tr([html.Th("Grade"), html.Th("Severity"),
                                       html.Th("Examples")])),
                   html.Tbody(rows)], size="sm", bordered=True),
    ], title="What is AIS? (injury severity scale)")], start_collapsed=True,
        className="mb-3")


layout = html.Div([
    html.H2("Restraint system analysis — injury assessment"),
    html.Div([
        html.Div(id=RESTRAINT_STATUS_ID, className="text-muted"),
        dbc.Button("Load example results", id="restraint-load-example",
                   color="secondary", outline=True, size="sm", className="ms-3",
                   title="Pre-computed VIVA+ frontal crash (no simulation needed)"),
    ], style={"alignItems": "center", "display": "flex"}, className="mb-3"),
    html.Div([
        html.Div([_button(key) for key in SECTION_IDS]),
        html.Div([
            html.Span("Occupant age (used for rib fractures): ",
                      className="me-2 small"),
            dcc.Dropdown(id=RESTRAINT_RIB_AGE_ID, clearable=False,
                         options=[{"label": f"{age} years", "value": age}
                                  for age in RIB_RISK_AGES],
                         value=RIB_RISK_AGES[1], style={"width": "130px"}),
        ], style={"alignItems": "center", "display": "flex"}, className="mb-3"),
    ]),
    html.Div([
        html.H3("Summary"),
        _plain("This page estimates how likely the occupant (VIVA+, an average-size "
               "adult male computer model of the human body) is to be injured in this "
               "simulated frontal crash. Green means a low chance, orange a medium "
               "chance and red a high chance of the injury named on the card."),
        html.Div(id="restraint-summary-cards"),
        _ais_explainer(),
        _graph("restraint-ais-graph",
               "Each bar is the estimated chance of an injury of at least the given "
               "severity. Darker bars are more severe injuries. Shaded background: "
               "green < 10 %, orange 10-50 %, red > 50 %."),
        html.H4("Compared with crash-test dummy limits"),
        dbc.Alert(INDICATIVE_NOTE, color="info"),
        html.Div(id="restraint-overview-table"),
        html.H4("What could not be assessed"),
        html.Div(id="restraint-unavailable"),
    ], id=SECTION_IDS["overview"]),
    html.Div([
        html.H3("Occupant motion"),
        _plain("A side view of the occupant's skeleton during the crash, drawn from "
               "the simulation. Press play or drag the slider to see how the head, "
               "spine, arm and leg move."),
        dcc.RadioItems(
            id="restraint-motion-frame", value="vehicle", inline=True,
            inputStyle={"marginRight": "6px", "marginLeft": "12px"},
            options=[{"label": "Seen from inside the car", "value": "vehicle"},
                     {"label": "Seen from the road (global coordinates)",
                      "value": "global"}]),
        _graph("restraint-motion-graph",
               "Points are anatomical landmarks of the VIVA+ model (left side). "
               "x: fore-aft position, z: height, both in mm. 'Inside the car' "
               "subtracts the motion of a vehicle-body node, so you see how the "
               "occupant moves relative to the seat and belt."),
    ], id=SECTION_IDS[MOTION], style={"display": "none"}),
    html.Div([
        html.H3("Head"),
        html.Div(id="restraint-head-plain"),
        html.Div(id="restraint-head-metrics"),
        _graph("restraint-head-risk-graph",
               "The curves show how the chance of head injury grows with HIC "
               "(NHTSA risk curves). The solid grey line is this crash. Background: "
               "green below 500 (Euro NCAP best rating), orange 500-700, red above "
               "700 (fails FMVSS 208 and Euro NCAP). A limit is not "
               "the point where injury becomes certain: it is the value regulators "
               "accept as low enough risk (about 11 % chance of a serious head "
               "injury at HIC 700). The risk keeps rising above the limit and gets "
               "close to, but never exactly, 100 %."),
        _graph("restraint-head-acceleration-graph",
               "How hard the head was accelerated over time, in g (1 g = gravity). "
               "HIC is computed from this curve."),
        _graph("restraint-head-omega-graph",
               "How fast the head rotated. Fast rotation strains the brain; BrIC "
               "and the VIVA+ DAMAGE metric are computed from this."),
    ], id=SECTION_IDS[HEAD], style={"display": "none"}),
    html.Div([
        html.H3("Neck"),
        html.Div(id="restraint-neck-plain"),
        html.Div(id="restraint-neck-metrics"),
        _graph("restraint-neck-nic-graph",
               "NIC compares head and upper-back motion. Above the red line minor "
               "neck injury (whiplash) becomes likely. NIC was developed for rear "
               "impacts, so in a frontal crash it is indicative only."),
        _graph("restraint-neck-acceleration-graph",
               "Fore-aft acceleration of the head and the upper back (T1 vertebra)."),
    ], id=SECTION_IDS[NECK], style={"display": "none"}),
    html.Div([
        html.H3("Chest"),
        html.Div(id="restraint-thorax-plain"),
        html.Div(id="restraint-thorax-metrics"),
        _graph("restraint-thorax-nfr-graph",
               "Chance of the number of broken ribs. 1 broken rib is AIS 1, 2 ribs "
               "AIS 2, 3 or more ribs AIS 3 (serious)."),
        _graph("restraint-thorax-deflection-graph",
               "How much the chest was compressed (breastbone towards the spine) "
               "over time, with crash-test dummy limits."),
        _graph("restraint-thorax-rib-strain-graph",
               "Highest stretch of the bone in each rib. Higher strain means a "
               "higher chance that the rib breaks."),
        _graph("restraint-thorax-rib-risk-graph",
               "Chance that each rib breaks for the selected age (Larsson 2021)."),
    ], id=SECTION_IDS[THORAX], style={"display": "none"}),
    html.Div([
        html.H3("Lower body"),
        html.Div(id="restraint-lower-plain"),
        html.Div(id="restraint-lower-metrics"),
        _graph("restraint-lower-pelvis-graph",
               "How hard the pelvis was accelerated, in g."),
        _graph("restraint-lower-spine-graph",
               "Force through each disc of the upper/middle back (thoracic spine). "
               "Positive: the spine is pulled apart, negative: it is compressed."),
    ], id=SECTION_IDS[LOWER], style={"display": "none"}),
    html.Div([
        html.H3("Engineering details"),
        html.Div(id="restraint-details-files", className="mb-3"),
        html.H4("All computed values"),
        html.Div(id="restraint-details-table"),
        dbc.Accordion([dbc.AccordionItem(
            dbc.Table([html.Tbody([html.Tr([html.Td(key), html.Td(text)])
                                   for key, text in SOURCES.items()])],
                      size="sm", bordered=True),
            title="References for limits and risk functions")],
            start_collapsed=True, className="mt-3"),
    ], id=SECTION_IDS["details"], style={"display": "none"}),
])
register_page(__name__, path=RESTRAINT_PAGE_PATH, layout=layout)


# --- Data helpers ------------------------------------------------------------
def _load_status(store: Optional[dict]) -> dict:
    if not store or not store.get("status_json"):
        return {}
    try:
        return json.loads(Path(store["status_json"]).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _unit_factor(unit: str) -> Tuple[float, str]:
    """Factor and display unit converting model units (mm, ms, kg) for people."""
    unit = unit.strip()
    if unit == "millimeter / millisecond ** 2":
        return 1000.0 / G, "g"
    if unit == "radian / millisecond":
        return 1000.0, "rad/s"
    if unit == "kilogram * millimeter / millisecond ** 2":
        return 1.0, "kN"
    if unit == "millimeter":
        return 1.0, "mm"
    if unit in ("dimensionless", ""):
        return 1.0, ""
    return 1.0, unit


def _signals(store: Optional[dict], region: str,
             pattern: str) -> List[Tuple[str, List[float], List[float], str]]:
    """Return (name, time, values, display unit) for matching visualizations."""
    path = (store or {}).get("region_csvs", {}).get(region)
    if not path or not Path(path).is_file():
        return []
    metadata, values = read_dynasaur_csv(path)
    regex = re.compile(pattern)
    found = []
    for column in range(1, metadata.shape[1]):
        name = str(metadata.iloc[1, column])
        label = str(metadata.iloc[2, column])
        if "time" in label.lower() or not regex.search(name):
            continue
        factor, unit = _unit_factor(str(metadata.iloc[METADATA_ROWS - 1, column]))
        found.append((name,
                      values.iloc[:, column - 1].tolist(),
                      [v * factor for v in values.iloc[:, column].tolist()],
                      unit))
    return found


_ROTATION_NAMES = {"x": "roll (tilting sideways)", "y": "pitch (nodding)",
                   "z": "yaw (turning)"}


def _friendly(name: str) -> str:
    """Readable legend label for a Dynasaur visualization name."""
    match = re.match(r"(.+)_(\d+)_axial$", name)
    if match:
        labels = load_hbm_dictionary().get("beam_set_labels", {}).get(match.group(1), [])
        index = int(match.group(2)) - 1
        level = labels[index] if index < len(labels) else f"#{index + 1}"
        return f"{level} disc"
    match = re.match(r"head_r([xyz])_velocity$", name)
    if match:
        return f"Head {_ROTATION_NAMES[match.group(1)]}"
    return {
        "head_resultant_acceleration_CFC1000": "Head (CFC 1000 filtered)",
        "pelvis_resultant_acceleration_CFC1000": "Pelvis (CFC 1000 filtered)",
        "head_x_acceleration": "Head",
        "T1_x_acceleration": "Upper back (T1 vertebra)",
        "NIC": "NIC",
    }.get(name, name.replace("_", " "))


def _time_figure(series, title: str, y_title: str,
                 colors: Optional[Sequence[str]] = None) -> go.Figure:
    figure = go.Figure()
    for index, (name, time, values, _unit) in enumerate(series):
        line = {"color": colors[index]} if colors else {}
        figure.add_trace(go.Scatter(x=time, y=values, mode="lines",
                                    name=_friendly(name), line=line))
    unit = series[0][3] if series else ""
    figure.update_layout(title=title, xaxis_title="time [ms]",
                         yaxis_title=f"{y_title} [{unit}]" if unit else y_title,
                         **GRAPH_LAYOUT)
    if not series:
        figure.add_annotation(text="No data available", showarrow=False,
                              xref="paper", yref="paper", x=0.5, y=0.5)
    return figure


def _metric_cards(items: Sequence[Tuple[str, Optional[float], str, str]]) -> dbc.Row:
    """Cards of (label, value, unit, plain-language hint)."""
    cards = []
    for label, value, unit, hint in items:
        if value is None:
            text = "n/a"
        elif unit == "%":
            text = f"{100 * value:.0f} %"
        else:
            text = f"{value:.3g} {unit}".strip()
        cards.append(dbc.Col(dbc.Card(dbc.CardBody([
            html.Div(label, className="text-muted small"),
            html.H4(text, className="mb-0",
                    style={"fontFamily": style.NUMERIC_FONT}),
            html.Div(hint, className="small text-muted") if hint else None,
        ]), className="h-100"), md=3, className="mb-2"))
    return dbc.Row(cards, className="mb-3")


def _values(status: dict) -> Dict[str, float]:
    merged = dict(status.get("criteria", {}))
    merged.update(status.get("derived", {}))
    return merged


def _get(values: Dict[str, float], key: str) -> Optional[float]:
    for name, value in values.items():
        if name == key or name.endswith(f"_{key}"):
            return value
    return None


def _band(probability: Optional[float]) -> Tuple[str, str]:
    if probability is None:
        return "Not assessed", "secondary"
    for upper, label, color in RISK_BANDS:
        if probability < upper:
            return label, color
    return RISK_BANDS[-1][1], RISK_BANDS[-1][2]


def _unavailable(status: dict, region: Optional[str] = None) -> html.Div:
    rows = [s for s in status.get("statuses", [])
            if not s.get("available") and (region is None or s.get("region") == region)]
    if not rows:
        return html.Div("All criteria in this section were evaluated.",
                        className="text-success")
    return dbc.Table(
        [html.Thead(html.Tr([html.Th("Region"), html.Th("Criterion"),
                             html.Th("Why / what to add to the simulation")]))]
        + [html.Tbody([html.Tr([html.Td(s["region"].title()), html.Td(s["name"]),
                                html.Td(s["missing_reason"])]) for s in rows])],
        bordered=True, size="sm",
    )


def _limit_badges(row: int, value: Optional[float],
                  limits: Dict[str, Limit]) -> html.Div:
    """Limits as badges: red when exceeded, green when met; source on hover."""
    badges = []
    for column, (label, limit) in enumerate(limits.items()):
        badge_id = f"restraint-limit-{row}-{column}"
        if value is None:
            color, verdict = "secondary", "not evaluated"
        elif value > limit.value:
            color, verdict = "danger", "exceeded"
        else:
            color, verdict = "success", "met"
        tip = [html.B(f"{label}: {limit.value:g} {limit.unit} ({verdict})"),
               html.Br(), SOURCES.get(limit.source, limit.source)]
        if limit.note:
            tip += [html.Br(), html.I(limit.note)]
        text = label if f"{limit.value:g}" in label else f"{label}: {limit.value:g}"
        badges.append(dbc.Badge(text, id=badge_id,
                                color=color, className="me-1 mb-1",
                                style={"cursor": "help", "fontSize": "0.85rem"}))
        badges.append(dbc.Tooltip(tip, target=badge_id, placement="top",
                                  style={"maxWidth": "420px", "textAlign": "left"}))
    return html.Div(badges)


def _rib_figure(values: Dict[str, float], suffix: str, title: str,
                y_title: str, percent: bool = False) -> go.Figure:
    figure = go.Figure()
    sides = style.side_colors()
    for side, label, color in (("L", "left ribs", sides["L"]),
                               ("R", "right ribs", sides["R"])):
        ribs, numbers = [], []
        for rib in range(1, 13):
            value = _get(values, f"TX-Ribcage-R{rib}-Cortical-{side}{suffix}")
            if value is not None:
                ribs.append(f"Rib {rib}")
                numbers.append(100 * value if percent else value)
        if ribs:
            figure.add_trace(go.Bar(x=ribs, y=numbers, name=label,
                                    marker_color=color))
    figure.update_layout(title=title, yaxis_title=y_title, barmode="group",
                         **GRAPH_LAYOUT)
    return figure


# --- Risk summaries ----------------------------------------------------------
def _risk_rows(values: Dict[str, float], age: int) -> List[Tuple[str, Dict[str, float]]]:
    """(body-region label, {AIS level: probability}) for the AIS chart."""
    rows = []
    head = {level: _get(values, f"HIC15_risk_{level}") for level in HIC_RISK_LOGNORMAL}
    rows.append(("Head (HIC)", head))
    rows.append(("Brain (VIVA+ DAMAGE)", {
        "AIS1+": _get(values, "DAMAGE_risk_AIS1"),
        "AIS2+": _get(values, "DAMAGE_risk_AIS2"),
        "AIS4+": _get(values, "DAMAGE_risk_AIS4+"),
    }))
    rows.append(("Neck (NIC, whiplash)", {"AIS1+": _get(values, "NIC_risk")}))
    rows.append((f"Chest (broken ribs, {age} y)", {
        f"AIS{level}+": _get(values, f"thorax_risk_AIS{level}+_{age}YO")
        for level in (1, 2, 3)}))
    return [(label, {k: v for k, v in risks.items() if v is not None})
            for label, risks in rows]


def _ais_figure(values: Dict[str, float], age: int) -> go.Figure:
    rows = _risk_rows(values, age)
    figure = go.Figure()
    for low, high, color in ((0, 10, style.BAND_FILL["low"]),
                             (10, 50, style.BAND_FILL["medium"]),
                             (50, 100, style.BAND_FILL["high"])):
        figure.add_hrect(y0=low, y1=high, fillcolor=color, line_width=0, layer="below")
    for level, color in AIS_COLORS.items():
        x = [label for label, risks in rows if level in risks]
        y = [100 * risks[level] for _label, risks in rows if level in risks]
        if not x:
            continue
        number = int(level[3])
        name = f"{level} {AIS_DESCRIPTIONS[number][0].lower()} or worse"
        figure.add_trace(go.Bar(
            x=x, y=y, name=name, marker_color=color,
            text=[f"{v:.0f} %" for v in y], textposition="outside",
            hovertemplate="%{x}<br>" + name + ": %{y:.1f} %<extra></extra>"))
    figure.update_layout(title="Injury risk by severity (AIS)", barmode="group",
                         xaxis=dict(categoryorder="array",
                                    categoryarray=[label for label, _r in rows]),
                         yaxis=dict(title="chance of injury [%]", range=[0, 112]),
                         **GRAPH_LAYOUT)
    return figure


def _summary_card(title: str, probability: Optional[float], headline: str,
                  details: Sequence[str]) -> dbc.Col:
    band, color = _band(probability)
    value = "–" if probability is None else f"{100 * probability:.0f} %"
    return dbc.Col(dbc.Card([
        dbc.CardHeader(html.Div([html.B(title),
                                 dbc.Badge(band, color=color, className="ms-2")])),
        dbc.CardBody([
            html.H2(value, className=f"text-{color} mb-1",
                    style={"fontFamily": style.NUMERIC_FONT}),
            html.Div(headline, className="mb-2"),
            html.Ul([html.Li(d, className="small text-muted") for d in details],
                    className="mb-0 ps-3"),
        ]),
    ], color=color, outline=True, className="h-100"), md=6, lg=3, className="mb-3")


def _pct(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{100 * value:.0f} %"


def _summary_cards(values: Dict[str, float], age: int) -> dbc.Row:
    hic = _get(values, "HIC15")
    expected_ribs = _get(values, f"expected_fractured_ribs_{age}YO")
    pelvis = _get(values, "pelvis_peak_resultant_acceleration")
    return dbc.Row([
        _summary_card(
            "Head", _get(values, "HIC15_risk_AIS3+"),
            "chance of a serious head injury (AIS 3+, e.g. skull fracture)",
            [f"HIC15 = {hic:.0f} (dummy limit 700)" if hic is not None else "HIC15 n/a",
             f"Brain injury AIS 4+ (VIVA+): {_pct(_get(values, 'DAMAGE_risk_AIS4+'))}"]),
        _summary_card(
            "Neck", _get(values, "NIC_risk"),
            "chance of a minor neck injury (AIS 1, whiplash-type)",
            ["NIC is a rear-impact measure: indicative only in a frontal crash",
             "Neck forces (Nij) not assessed: no neck load cell in the simulation"]),
        _summary_card(
            "Chest", _get(values, f"thorax_risk_AIS3+_{age}YO"),
            f"chance of a serious chest injury (3+ broken ribs, AIS 3+) at age {age}",
            [f"Expected number of broken ribs: {expected_ribs:.1f}"
             if expected_ribs is not None else "Rib fractures n/a",
             f"Chest compression: {_get(values, 'chest_deflection_max') or 0:.0f} mm"]),
        _summary_card(
            "Lower body", None,
            "no injury risk function available for this simulation",
            [f"Pelvis peak acceleration: {pelvis:.0f} g" if pelvis else "Pelvis n/a",
             "Femur and lumbar forces need load cells in the simulation"]),
    ])


def _hic_risk_figure(hic: Optional[float]) -> go.Figure:
    figure = go.Figure()
    top = max(2000.0, 1.25 * hic) if hic else 2000.0
    xs = [top * i / 300 for i in range(1, 301)]
    for level, (_mu, _sigma) in HIC_RISK_LOGNORMAL.items():
        figure.add_trace(go.Scatter(
            x=xs, y=[100 * hic_risk(x, level) for x in xs], mode="lines",
            name=f"{level} {AIS_DESCRIPTIONS[int(level[3])][0].lower()} or worse",
            line=dict(color=AIS_COLORS[level], width=3)))
    # Limit zones instead of overlapping vertical labels.
    good = HIC15_LIMITS["Euro NCAP higher"].value
    limit = HIC15_LIMITS["FMVSS 208"].value
    for x0, x1, fill in ((0, good, style.BAND_FILL["low"]),
                         (good, limit, style.BAND_FILL["medium"]),
                         (limit, top, style.BAND_FILL["high"])):
        figure.add_vrect(x0=x0, x1=x1, fillcolor=fill, line_width=0, layer="below")
    # What the limit itself means in terms of risk.
    at_limit = [f"{level}: {100 * hic_risk(limit, level):.0f} %"
                for level in HIC_RISK_LOGNORMAL]
    figure.add_vline(x=limit, line_dash="dot", line_color=style.DANGER)
    figure.add_annotation(
        x=limit, y=100 * hic_risk(limit, "AIS3+"), xanchor="left", ax=40, ay=-60,
        text="Risk at the 700 limit<br>" + "<br>".join(at_limit),
        showarrow=True, arrowcolor=style.DANGER, font=dict(size=11),
        bgcolor=style.ANNOTATION_BG, align="left")
    if hic:
        figure.add_vline(x=hic, line_color=style.NEUTRAL, line_width=2,
                         annotation_text=f"this crash: HIC {hic:.0f}",
                         annotation_position="top left")
        for level in HIC_RISK_LOGNORMAL:
            risk = 100 * hic_risk(hic, level)
            figure.add_trace(go.Scatter(
                x=[hic], y=[risk], mode="markers+text", showlegend=False,
                marker=dict(size=11, color=AIS_COLORS[level],
                            line=dict(color=style.NEUTRAL, width=1)),
                text=[f"{risk:.0f} %"], textposition="middle right"))
    figure.update_layout(title="Head injury risk curves (HIC15)",
                         xaxis_title="HIC15 [-]",
                         yaxis=dict(title="chance of injury [%]", range=[0, 105]),
                         **GRAPH_LAYOUT)
    return figure


def _nfr_figure(values: Dict[str, float], age: int) -> go.Figure:
    """P(at least k broken ribs) with AIS bands."""
    figure = go.Figure()
    xs, ys, colors = [], [], []
    for level in (1, 2, 3):
        probability = _get(values, f"thorax_risk_AIS{level}+_{age}YO")
        if probability is None:
            continue
        xs.append(f"≥ {level} broken rib{'s' if level > 1 else ''}<br>(AIS {level}+)")
        ys.append(100 * probability)
        colors.append(AIS_COLORS[f"AIS{level}+"])
    figure.add_trace(go.Bar(x=xs, y=ys, marker_color=colors,
                            text=[f"{v:.0f} %" for v in ys], textposition="outside"))
    figure.update_layout(title=f"Broken ribs and chest injury severity (age {age})",
                         yaxis=dict(title="chance [%]", range=[0, 112]),
                         showlegend=False, **GRAPH_LAYOUT)
    return figure


def _deflection_figure(store: Optional[dict], status: dict) -> go.Figure:
    figure = go.Figure()
    coordinates = {name: (time, values)
                   for name, time, values, _unit in _signals(store, THORAX, r"_coordinate$")}
    roles = load_hbm_dictionary().get("nodes", {})
    sternum, spine = roles.get("sternum_mid"), roles.get("chest_spine_reference")
    try:
        time = coordinates[f"{sternum}_x_coordinate"][0]
        a = [coordinates[f"{sternum}_{axis}_coordinate"][1] for axis in "xyz"]
        b = [coordinates[f"{spine}_{axis}_coordinate"][1] for axis in "xyz"]
    except KeyError:
        figure.add_annotation(text="No data available", showarrow=False,
                              xref="paper", yref="paper", x=0.5, y=0.5)
        return figure
    distance = [math.sqrt(sum((a[i][k] - b[i][k]) ** 2 for i in range(3)))
                for k in range(len(time))]
    deflection = [distance[0] - d for d in distance]
    figure.add_trace(go.Scatter(x=time, y=deflection, mode="lines",
                                name="Chest compression (mid-sternum to T8)",
                                line=dict(width=3, color=style.SECTION_COLORS["thorax"])))
    for label, limit in CHEST_DEFLECTION_LIMITS.items():
        figure.add_hline(y=limit.value, line_dash="dash",
                         line_color=LIMIT_COLORS.get(limit.band, style.NEUTRAL),
                         annotation_text=f"{label} ({limit.value:g} mm)",
                         annotation_position="top left")
    figure.update_layout(title="Chest compression", xaxis_title="time [ms]",
                         yaxis_title="compression [mm]", **GRAPH_LAYOUT)
    return figure


def _motion_figure(store: Optional[dict], frame: str = "vehicle") -> go.Figure:
    """Side-view stick-figure animation from landmark coordinates."""
    signals = {name: (time, values)
               for name, time, values, _unit in _signals(store, MOTION, r"_coordinate$")}
    reference = {axis: signals.pop(f"{VEHICLE_REFERENCE}_{axis}_coordinate", None)
                 for axis in "xz"}
    relative = frame == "vehicle" and all(reference.values())
    if relative:
        for name, (time_, values_) in list(signals.items()):
            axis = name.rsplit("_", 2)[-2]
            ref = reference[axis][1]
            signals[name] = (time_, [v - (r - ref[0]) for v, r in zip(values_, ref)])
    chains = load_hbm_dictionary().get("motion_chains", {})
    figure = go.Figure()
    if not signals:
        figure.add_annotation(
            text="No motion data. Re-run the analysis to create it.",
            showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
        return figure

    def track(node: str, axis: str) -> Optional[List[float]]:
        entry = signals.get(f"{node}_{axis}_coordinate")
        return entry[1] if entry else None

    time = next(iter(signals.values()))[0]
    steps = list(range(0, len(time), max(1, len(time) // 60)))
    chain_tracks = {}
    for chain, nodes in chains.items():
        points = [(track(n, "x"), track(n, "z")) for n in nodes]
        chain_tracks[chain] = [p for p in points if p[0] and p[1]]
    colors = style.BODY_COLORS
    head = (track(chains.get("Spine", [""])[0], "x"),
            track(chains.get("Spine", [""])[0], "z"))

    def frame_traces(k: int) -> List[go.Scatter]:
        traces = [go.Scatter(
            x=[p[0][k] for p in points], y=[p[1][k] for p in points],
            mode="lines+markers", name=chain,
            line=dict(color=colors.get(chain, style.NEUTRAL), width=4),
            marker=dict(size=6)) for chain, points in chain_tracks.items()]
        if head[0]:
            traces.append(go.Scatter(x=[head[0][k]], y=[head[1][k]], mode="markers",
                                     name="Head", marker=dict(size=34,
                                     color=style.HEAD_FILL,
                                     line=dict(color=colors["Head"], width=2))))
        return traces

    for trace in frame_traces(0):
        figure.add_trace(trace)
    if head[0]:
        figure.add_trace(go.Scatter(x=head[0], y=head[1], mode="lines",
                                    name="Head path", line=dict(color=colors["Head"],
                                                                dash="dot", width=1)))
    figure.frames = [go.Frame(name=f"{time[k]:.0f}", data=frame_traces(k),
                              traces=list(range(len(chain_tracks) + (1 if head[0] else 0))))
                     for k in steps]
    all_x = [v for points in chain_tracks.values() for p in points for v in p[0]]
    all_z = [v for points in chain_tracks.values() for p in points for v in p[1]]
    pad = 80
    figure.update_layout(
        title="Occupant motion (side view, "
              + ("relative to the car)" if relative else "global coordinates)"),
        xaxis=dict(title="x [mm]", range=[min(all_x) - pad, max(all_x) + pad]),
        yaxis=dict(title="z [mm]", range=[min(all_z) - pad, max(all_z) + pad],
                   scaleanchor="x", scaleratio=1),
        height=650,
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
        updatemenus=[dict(type="buttons", showactive=False, x=0, y=-0.08,
                          xanchor="left", yanchor="top", direction="left", buttons=[
            dict(label="▶ Play", method="animate",
                 args=[None, dict(frame=dict(duration=80, redraw=True),
                                  transition=dict(duration=0), fromcurrent=True)]),
            dict(label="❚❚ Pause", method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False),
                                    mode="immediate")]),
        ])],
        sliders=[dict(active=0, x=0.18, len=0.82, y=-0.06,
                      currentvalue=dict(prefix="time: ", suffix=" ms"),
                      steps=[dict(method="animate", label=frame.name,
                                  args=[[frame.name], dict(mode="immediate",
                                        frame=dict(duration=0, redraw=True))])
                             for frame in figure.frames])],
        margin=dict(l=60, r=20, t=80, b=110),
    )
    return figure


def _all_values_table(store: Optional[dict]) -> html.Div:
    rows = []
    for key in ("criteria_csv", "derived_csv"):
        path = (store or {}).get(key)
        if not path or not Path(path).is_file():
            continue
        metadata, values = read_dynasaur_csv(path)
        for column in range(metadata.shape[1]):
            value = values.iloc[0, column] if not values.empty else None
            rows.append(html.Tr([
                html.Td(str(metadata.iloc[0, column]).title()),
                html.Td(str(metadata.iloc[2, column])),
                html.Td("n/a" if value is None or value != value else f"{value:.5g}"),
                html.Td(str(metadata.iloc[3, column]).replace("dimensionless", "-")),
                html.Td("Dynasaur" if key == "criteria_csv" else "HIVE (Python)"),
            ]))
    if not rows:
        return html.Div("No values available.")
    return dbc.Table([html.Thead(html.Tr([html.Th("Region"), html.Th("Name"),
                                          html.Th("Value"), html.Th("Unit"),
                                          html.Th("Computed by")])),
                      html.Tbody(rows)], size="sm", bordered=True, striped=True)


# --- Callbacks ---------------------------------------------------------------
def register_callbacks(app: Dash) -> None:
    """Connect the main-page button and the restraint page plots."""

    @app.callback(
        Output(RESTRAINT_RESULTS_STORE_ID, "data"),
        Output("url", "pathname", allow_duplicate=True),
        Input(RESTRAINT_BUTTON_ID, "n_clicks"),
        prevent_initial_call=True,
    )
    def start_restraint_analysis(n_clicks: Optional[int]):
        if not n_clicks:
            return no_update, no_update
        from restraint_system_analysis.pipeline import main as run_pipeline
        try:
            results = run_pipeline()
        except Exception as error:  # report any backend failure on the page
            return {"error": f"{type(error).__name__}: {error}"}, RESTRAINT_PAGE_PATH
        if results is None:
            return no_update, no_update
        return results.to_store(), RESTRAINT_PAGE_PATH

    @app.callback(
        Output(RESTRAINT_RESULTS_STORE_ID, "data", allow_duplicate=True),
        Input("restraint-load-example", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_example(n_clicks: Optional[int]):
        if not n_clicks:
            raise PreventUpdate
        from restraint_system_analysis.example import example_results
        try:
            return example_results().to_store()
        except OSError as error:
            return {"error": f"{type(error).__name__}: {error}"}

    @app.callback(
        Output(PROGRESS_OVERLAY_ID, "style"),
        Output("restraint-progress-bar", "value"),
        Output("restraint-progress-bar", "label"),
        Output("restraint-progress-message", "children"),
        Output("restraint-progress-elapsed", "children"),
        Input("restraint-progress-interval", "n_intervals"),
        State(PROGRESS_OVERLAY_ID, "style"),
    )
    def poll_progress(_n, current_style):
        from restraint_system_analysis import progress
        state = progress.snapshot()
        if not state["active"]:
            if current_style == _OVERLAY_HIDDEN:
                raise PreventUpdate
            return _OVERLAY_HIDDEN, 0, "", "", ""
        percent = round(100 * float(state["fraction"]))
        minutes, seconds = divmod(int(state["elapsed"]), 60)
        return (_OVERLAY_SHOWN, percent, f"{percent} %", state["message"],
                f"Elapsed {minutes:d}:{seconds:02d}")

    @app.callback(
        [Output(section_id, "style") for section_id in SECTION_IDS.values()],
        [Input(f"restraint-{key.lower()}-button", "n_clicks") for key in SECTION_IDS],
    )
    def show_section(*_clicks):
        triggered = str(ctx.triggered_id or "restraint-overview-button")
        visible = next((key for key in SECTION_IDS
                        if triggered == f"restraint-{key.lower()}-button"), "overview")
        return [{"display": "block"} if key == visible else {"display": "none"}
                for key in SECTION_IDS]

    @app.callback(
        Output(RESTRAINT_STATUS_ID, "children"),
        Output("restraint-summary-cards", "children"),
        Output("restraint-ais-graph", "figure"),
        Output("restraint-overview-table", "children"),
        Output("restraint-unavailable", "children"),
        Input(RESTRAINT_RESULTS_STORE_ID, "data"),
        Input(RESTRAINT_RIB_AGE_ID, "value"),
    )
    def update_overview(store: Optional[dict], age: int):
        if not store:
            return ("No analysis run yet. Start it from the main page.",
                    None, go.Figure(), None, None)
        if store.get("error"):
            return (dbc.Alert(f"Analysis failed: {store['error']}", color="danger"),
                    None, go.Figure(), None, None)
        status = _load_status(store)
        values = _values(status)
        rows = [
            ("HIC15", _get(values, "HIC15"), "-", HIC15_LIMITS),
            ("BrIC", _get(values, "BrIC"), "-", BRIC_LIMITS),
            ("NIC max", _get(values, "NIC_max"), "m²/s²", NIC_LIMITS),
            ("Chest deflection", _get(values, "chest_deflection_max"), "mm",
             CHEST_DEFLECTION_LIMITS),
        ]
        table = html.Div([
            dbc.Table(
                [html.Thead(html.Tr([html.Th("Criterion"), html.Th("Value"),
                                     html.Th("Limits (indicative)")]))]
                + [html.Tbody([html.Tr([
                    html.Td(name),
                    html.Td("n/a" if value is None else f"{value:.3g} {unit}"),
                    html.Td(_limit_badges(index, value, limits)),
                ]) for index, (name, value, unit, limits) in enumerate(rows)])],
                bordered=True, size="sm",
            ),
            html.Div("Red: limit exceeded · green: limit met · hover a limit for "
                     "its source.", className="text-muted small mb-3"),
        ])
        if status.get("example"):
            message = html.Span([html.B("Example results: "),
                                 status.get("simulation_dir", "")],
                                className="text-info")
        else:
            message = f"Results in {store.get('output_dir')}"
        return (message, _summary_cards(values, age), _ais_figure(values, age),
                table, _unavailable(status))

    @app.callback(
        Output("restraint-motion-graph", "figure"),
        Input(RESTRAINT_RESULTS_STORE_ID, "data"),
        Input("restraint-motion-frame", "value"),
    )
    def update_motion(store: Optional[dict], frame: str):
        return _motion_figure(store, frame)

    @app.callback(
        Output("restraint-head-plain", "children"),
        Output("restraint-head-metrics", "children"),
        Output("restraint-head-risk-graph", "figure"),
        Output("restraint-head-acceleration-graph", "figure"),
        Output("restraint-head-omega-graph", "figure"),
        Input(RESTRAINT_RESULTS_STORE_ID, "data"),
    )
    def update_head(store: Optional[dict]):
        status = _load_status(store)
        values = _values(status)
        hic = _get(values, "HIC15")
        risk = _get(values, "HIC15_risk_AIS3+")
        plain = _plain(
            "HIC measures how violently the head is shaken by a blow; crash-test "
            "dummies must stay below 700. "
            + (f"Here HIC is {hic:.0f}, which corresponds to a {_pct(risk)} chance of a "
               "serious head injury." if hic is not None else "HIC was not evaluated.")
            + " BrIC and DAMAGE describe brain strain from head rotation.")
        cards = _metric_cards([
            ("HIC15", hic, "", "head impact severity (limit 700)"),
            ("Serious head injury (AIS 3+)", risk, "%", "from HIC (NHTSA)"),
            ("BrIC", _get(values, "BrIC"), "", "brain rotation (1.0 = critical)"),
            ("Peak head acceleration",
             _get(values, "head_peak_resultant_acceleration"), "g", "1 g = gravity"),
            ("Brain injury AIS 1+ (DAMAGE)", _get(values, "DAMAGE_risk_AIS1"), "%",
             "VIVA+ risk function"),
            ("Brain injury AIS 2+ (DAMAGE)", _get(values, "DAMAGE_risk_AIS2"), "%",
             "VIVA+ risk function"),
            ("Brain injury AIS 4+ (DAMAGE)", _get(values, "DAMAGE_risk_AIS4+"), "%",
             "VIVA+ risk function"),
            ("DAMAGE", _get(values, "DAMAGE"), "", "maximum brain strain proxy"),
        ])
        return (
            plain,
            html.Div([cards, _unavailable(status, HEAD)]),
            _hic_risk_figure(hic),
            _time_figure(_signals(store, HEAD, r"resultant_acceleration"),
                         "Head acceleration", "acceleration"),
            _time_figure(_signals(store, HEAD, r"head_r[xyz]_velocity"),
                         "Head rotation speed (head-fixed axes)", "angular velocity"),
        )

    @app.callback(
        Output("restraint-neck-plain", "children"),
        Output("restraint-neck-metrics", "children"),
        Output("restraint-neck-nic-graph", "figure"),
        Output("restraint-neck-acceleration-graph", "figure"),
        Input(RESTRAINT_RESULTS_STORE_ID, "data"),
    )
    def update_neck(store: Optional[dict]):
        status = _load_status(store)
        values = _values(status)
        nic = _get(values, "NIC_max")
        plain = _plain(
            "NIC measures the whip-like motion between head and upper back. Values "
            "above 15 suggest a risk of minor neck injury. "
            + (f"Here NIC is {nic:.0f}." if nic is not None else "NIC was not evaluated."))
        cards = _metric_cards([
            ("NIC max", nic, "m²/s²", "tolerance 15"),
            ("Minor neck injury (AIS 1)", _get(values, "NIC_risk"), "%",
             "VIVA+ risk function"),
        ])
        nic_series = _signals(store, NECK, r"(^|_)NIC$")
        figure = _time_figure(nic_series, "Neck Injury Criterion over time", "NIC")
        for label, limit in NIC_LIMITS.items():
            figure.add_hline(y=limit.value, line_dash="dash", line_color=style.DANGER,
                             annotation_text=f"{label} ({limit.value:g})")
        return (
            plain,
            html.Div([cards, _unavailable(status, NECK)]),
            figure,
            _time_figure(_signals(store, NECK, r"x_acceleration"),
                         "Head and upper-back acceleration (fore-aft)", "acceleration"),
        )

    @app.callback(
        Output("restraint-thorax-plain", "children"),
        Output("restraint-thorax-metrics", "children"),
        Output("restraint-thorax-nfr-graph", "figure"),
        Output("restraint-thorax-deflection-graph", "figure"),
        Output("restraint-thorax-rib-strain-graph", "figure"),
        Output("restraint-thorax-rib-risk-graph", "figure"),
        Input(RESTRAINT_RESULTS_STORE_ID, "data"),
        Input(RESTRAINT_RIB_AGE_ID, "value"),
    )
    def update_thorax(store: Optional[dict], age: int):
        status = _load_status(store)
        values = _values(status)
        expected = _get(values, f"expected_fractured_ribs_{age}YO")
        serious = _get(values, f"thorax_risk_AIS3+_{age}YO")
        plain = _plain(
            "The seat belt loads the chest. Older bones break more easily, so the "
            "risk depends on the age chosen at the top of the page. "
            + (f"For a {age}-year-old about {expected:.1f} ribs are expected to break; "
               f"the chance of 3 or more broken ribs (serious, AIS 3) is "
               f"{_pct(serious)}." if expected is not None else ""))
        cards = _metric_cards([
            ("Chest compression", _get(values, "chest_deflection_max"), "mm",
             "mid-sternum to T8"),
            ("Expected broken ribs", expected, "", f"age {age}"),
            ("At least 1 broken rib", _get(values, f"thorax_risk_AIS1+_{age}YO"), "%",
             "AIS 1+"),
            ("3 or more broken ribs", serious, "%", "AIS 3+ (serious)"),
        ])
        return (
            plain,
            html.Div([cards, _unavailable(status, THORAX)]),
            _nfr_figure(values, age),
            _deflection_figure(store, status),
            _rib_figure(values, "_max_strain", "Peak tensile strain per rib",
                        "strain [-]"),
            _rib_figure(values, f"_fracture_risk_{age}YO",
                        f"Chance of fracture per rib, age {age}", "chance [%]",
                        percent=True),
        )

    @app.callback(
        Output("restraint-lower-plain", "children"),
        Output("restraint-lower-metrics", "children"),
        Output("restraint-lower-pelvis-graph", "figure"),
        Output("restraint-lower-spine-graph", "figure"),
        Input(RESTRAINT_RESULTS_STORE_ID, "data"),
    )
    def update_lower(store: Optional[dict]):
        status = _load_status(store)
        values = _values(status)
        plain = _plain(
            "No injury risk can be given for the legs and lower back yet: the "
            "simulation has no virtual load cells there. The pelvis acceleration and "
            "the forces in the spine discs are shown for engineers.")
        cards = _metric_cards([
            ("Pelvis peak acceleration",
             _get(values, "pelvis_peak_resultant_acceleration"), "g", "1 g = gravity"),
            ("Thoracic spine max tension", _get(values, "spine_beam_max_tension"), "kN",
             "discs pulled apart"),
            ("Thoracic spine max compression",
             _get(values, "spine_beam_max_compression"), "kN", "discs pressed together"),
        ])
        spine = _signals(store, LOWER, r"_axial$")
        colors = sample_colorscale("Viridis", [i / max(len(spine) - 1, 1)
                                               for i in range(len(spine))])
        spine_figure = _time_figure(spine, "Thoracic spine disc forces (top to bottom)",
                                    "axial force", colors=colors)
        spine_figure.update_layout(legend_title_text="Disc level:")
        return (
            plain,
            html.Div([cards, _unavailable(status, LOWER)]),
            _time_figure(_signals(store, LOWER, r"pelvis"),
                         "Pelvis acceleration", "acceleration"),
            spine_figure,
        )

    @app.callback(
        Output("restraint-details-files", "children"),
        Output("restraint-details-table", "children"),
        Input(RESTRAINT_RESULTS_STORE_ID, "data"),
    )
    def update_details(store: Optional[dict]):
        if not store or store.get("error"):
            return None, None
        files = [store.get("criteria_csv"), store.get("derived_csv"),
                 store.get("status_json")] + list(store.get("region_csvs", {}).values())
        listing = html.Div([
            html.Div("Output files (open in Excel / Python):", className="small"),
            html.Ul([html.Li(html.Code(f), className="small") for f in files if f]),
        ])
        return listing, _all_values_table(store)
