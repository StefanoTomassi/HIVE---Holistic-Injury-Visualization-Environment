"""Visual settings of the restraint page, following ``Style instructions.md``.

The global look comes from the active HIVE theme (``GUI/theme/hive_theme.py``):
fonts, backgrounds, grid, legend, hover and the Plotly template are inherited
automatically. This module only holds what that theme does not provide, so that
no colour is hard-coded inside ``restraint_page.py``:

* semantic status colours (style guide, "HIVE Clinical" / "Safety Assessment"):
  green, amber and red are used **only** to express risk, never as decoration;
* a sequential palette for injury severity (AIS 1 -> 4+, light -> dark);
* the section and body-part colours, taken from the same colour-blind-safe
  palette as the whiplash page;
* graph configuration with SVG export from the modebar.
"""

from typing import Dict, List

import plotly.io as pio

# --- Semantic status colours (style guide, palette of proposal 1) ------------
SUCCESS = "#1f9d55"
WARNING = "#d97706"
DANGER = "#d64545"
NEUTRAL = "#5f6b76"

#: Transparent fills for risk bands drawn behind bar charts.
BAND_FILL = {
    "low": "rgba(31, 157, 85, 0.08)",
    "medium": "rgba(217, 119, 6, 0.08)",
    "high": "rgba(214, 69, 69, 0.08)",
}

#: Limit lines: regulatory/tolerance = red, lower performance = amber,
#: higher performance = green.
LIMIT_COLORS = {
    "regulatory": DANGER,
    "tolerance": DANGER,
    "lower_performance": WARNING,
    "higher_performance": SUCCESS,
}

#: Sequential severity palette (light -> dark) so that worse = darker.
AIS_COLORS = {
    "AIS1+": "#f6c87a",
    "AIS2+": WARNING,
    "AIS3+": DANGER,
    "AIS4+": "#7a1f1f",
}

# --- Categorical colours (same Okabe-Ito based set as the whiplash page) -----
SECTION_COLORS = {
    "overview": "#0173b2",
    "motion": "#56b4e9",
    "head": "#d55e00",
    "neck": "#029e73",
    "thorax": "#cc78bc",
    "lower": "#ca9161",
    "details": NEUTRAL,
}
BODY_COLORS = {
    "Spine": "#0173b2",
    "Chest": "#cc78bc",
    "Arm": "#029e73",
    "Pelvis": "#ca9161",
    "Leg": "#d55e00",
    "Head": "#d55e00",
}
HEAD_FILL = "rgba(213, 94, 0, 0.35)"
OVERLAY_BACKDROP = "rgba(23, 34, 43, 0.45)"
ANNOTATION_BG = "rgba(255, 255, 255, 0.85)"

#: Monospace font for numeric values (style guide: "Numeric values: mono").
NUMERIC_FONT = '"JetBrains Mono", Consolas, monospace'


def colorway() -> List[str]:
    """Trace colour cycle of the active HIVE Plotly template."""
    template = pio.templates[pio.templates.default]
    colors = list(template.layout.colorway or [])
    return colors or ["#0057b8", "#00a3a3", "#1f9d55", "#d97706", "#d64545"]


def side_colors() -> Dict[str, str]:
    """Colours for left/right comparisons, taken from the theme colour cycle."""
    colors = colorway()
    return {"L": colors[0], "R": colors[1 % len(colors)]}


def graph_config(filename: str) -> dict:
    """dcc.Graph config: modebar with SVG export (style guide requirement)."""
    return {
        "displayModeBar": True,
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {"format": "svg", "filename": filename, "scale": 2},
    }
