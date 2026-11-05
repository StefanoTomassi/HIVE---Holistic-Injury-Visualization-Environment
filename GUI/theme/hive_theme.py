"""Centralized visual themes for the HIVE Dash application."""

from dataclasses import dataclass
from typing import Dict, Mapping

import dash_bootstrap_components as dbc
import plotly.io as pio
from plotly.graph_objects import layout


@dataclass(frozen=True)
class HiveTheme:
    """Web and Plotly settings for one HIVE visual style."""

    name: str
    bootstrap_theme: str
    css: str
    plotly_template: str
    plotly_layout: Mapping[str, object]


def _css(
    background: str,
    surface: str,
    text: str,
    muted: str,
    primary: str,
    primary_hover: str,
    border: str,
    heading: str,
    font: str,
) -> str:
    return f"""
:root {{
    --hive-bg: {background};
    --hive-surface: {surface};
    --hive-text: {text};
    --hive-muted: {muted};
    --hive-primary: {primary};
    --hive-primary-hover: {primary_hover};
    --hive-border: {border};
    --hive-heading: {heading};
    --hive-font: {font};
}}

body {{
    background-color: var(--hive-bg);
    color: var(--hive-text);
    font-family: var(--hive-font);
}}

h1, h2, h3, h4, h5, h6 {{
    color: var(--hive-heading);
    font-family: var(--hive-font);
}}

.hive-app-header {{
    background-color: var(--hive-surface);
    border-bottom: 1px solid var(--hive-border);
    color: var(--hive-heading);
    padding: 12px 18px;
}}

.hive-section-button,
.btn-primary {{
    background-color: var(--hive-primary);
    border-color: var(--hive-primary);
    color: #ffffff;
    font-family: var(--hive-font);
}}

.hive-section-button:hover,
.btn-primary:hover {{
    background-color: var(--hive-primary-hover);
    border-color: var(--hive-primary-hover);
    color: #ffffff;
}}

.card, .accordion-item, .dash-dropdown {{
    background-color: var(--hive-surface);
    border-color: var(--hive-border);
}}

.text-muted {{
    color: var(--hive-muted) !important;
}}
"""


def _plotly_layout(
    *,
    paper_bgcolor: str,
    plot_bgcolor: str,
    font_family: str,
    font_color: str,
    colorway: list,
    gridcolor: str,
    linecolor: str,
    margin: Mapping[str, int],
    hovermode: str = "x unified",
    showgrid: bool = True,
    legend_bgcolor: str = "rgba(255,255,255,0.85)",
    legend_bordercolor: str = "#d9e2ec",
    modebar_bgcolor: str = "rgba(0,0,0,0)",
    modebar_color: str = "#5f6b76",
    modebar_activecolor: str = "#0057b8",
) -> Mapping[str, object]:
    """Build the reusable Plotly settings shared by every HIVE proposal."""
    axis = {
        "showgrid": showgrid,
        "gridcolor": gridcolor,
        "gridwidth": 1,
        "linecolor": linecolor,
        "linewidth": 1,
        "tickfont": {"family": font_family, "size": 12, "color": font_color},
        "title": {
            "font": {"family": font_family, "size": 13, "color": font_color}
        },
    }
    return {
        "paper_bgcolor": paper_bgcolor,
        "plot_bgcolor": plot_bgcolor,
        "font": {"family": font_family, "size": 13, "color": font_color},
        "title": {
            "font": {"family": font_family, "size": 17, "color": font_color},
            "x": 0.01,
            "xanchor": "left",
        },
        "colorway": colorway,
        "margin": dict(margin),
        "legend": {
            "bgcolor": legend_bgcolor,
            "bordercolor": legend_bordercolor,
            "borderwidth": 1,
            "font": {"family": font_family, "size": 12, "color": font_color},
        },
        "hoverlabel": {
            "bgcolor": paper_bgcolor,
            "bordercolor": linecolor,
            "font": {"family": font_family, "size": 12, "color": font_color},
        },
        "hovermode": hovermode,
        "modebar": {
            "bgcolor": modebar_bgcolor,
            "color": modebar_color,
            "activecolor": modebar_activecolor,
        },
        "xaxis": dict(axis),
        "yaxis": dict(axis),
    }


THEMES: Dict[str, HiveTheme] = {
    "clinical": HiveTheme(
        name="HIVE Clinical",
        bootstrap_theme=dbc.themes.MINTY,
        css=_css(
            "#f7f9fb",
            "#ffffff",
            "#17222b",
            "#5f6b76",
            "#0057b8",
            "#00438f",
            "#d9e2ec",
            "#17222b",
            '"Inter", "Segoe UI", Arial, sans-serif',
        ),
        plotly_template="hive_clinical",
        plotly_layout=_plotly_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_family="Inter, Arial, sans-serif",
            font_color="#17222b",
            colorway=["#0057b8", "#00a3a3", "#1f9d55", "#d97706", "#d64545"],
            gridcolor="#e5eaef",
            linecolor="#d9e2ec",
            margin={"l": 70, "r": 30, "t": 60, "b": 60},
            modebar_activecolor="#0057b8",
        ),
    ),
    "engineering_console": HiveTheme(
        name="HIVE Engineering Console",
        bootstrap_theme=dbc.themes.FLATLY,
        css=_css(
            "#eef1f4",
            "#ffffff",
            "#111827",
            "#6b7280",
            "#2563eb",
            "#1d4ed8",
            "#d1d5db",
            "#111827",
            '"Inter", "Segoe UI", Arial, sans-serif',
        ),
        plotly_template="hive_engineering_console",
        plotly_layout=_plotly_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_family="Inter, Arial, sans-serif",
            font_color="#111827",
            colorway=["#2563eb", "#f59e0b", "#16a34a", "#d97706", "#dc2626"],
            gridcolor="#e5e7eb",
            linecolor="#cbd5e1",
            margin={"l": 55, "r": 20, "t": 45, "b": 45},
            modebar_activecolor="#2563eb",
        ),
    ),
    "safety_assessment": HiveTheme(
        name="HIVE Safety Assessment",
        bootstrap_theme=dbc.themes.MINTY,
        css=_css(
            "#f6f8fa",
            "#ffffff",
            "#17222b",
            "#5f6b76",
            "#0f766e",
            "#0b5b54",
            "#d9e2ec",
            "#17222b",
            '"Inter", "Segoe UI", Arial, sans-serif',
        ),
        plotly_template="hive_safety_assessment",
        plotly_layout=_plotly_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_family="Inter, Arial, sans-serif",
            font_color="#17222b",
            colorway=["#1f9d55", "#d97706", "#d64545", "#0f766e", "#334155"],
            gridcolor="#e5eaef",
            linecolor="#d9e2ec",
            margin={"l": 70, "r": 30, "t": 60, "b": 60},
            modebar_activecolor="#0f766e",
        ),
    ),
    "scandinavian_minimal": HiveTheme(
        name="HIVE Scandinavian Minimal",
        bootstrap_theme=dbc.themes.LUX,
        css=_css(
            "#fafafa",
            "#ffffff",
            "#141414",
            "#6b6b6b",
            "#003057",
            "#00213d",
            "#e0e0e0",
            "#141414",
            '"Inter", "Segoe UI", Arial, sans-serif',
        ),
        plotly_template="hive_scandinavian_minimal",
        plotly_layout=_plotly_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_family="Inter, Arial, sans-serif",
            font_color="#141414",
            colorway=["#003057", "#006d77"],
            gridcolor="#e0e0e0",
            linecolor="#e0e0e0",
            margin={"l": 75, "r": 35, "t": 70, "b": 65},
            showgrid=False,
            legend_bgcolor="rgba(255,255,255,0.95)",
            legend_bordercolor="#e0e0e0",
            modebar_activecolor="#003057",
        ),
    ),
    "dark_analysis": HiveTheme(
        name="HIVE Dark Analysis",
        bootstrap_theme=dbc.themes.DARKLY,
        css=_css(
            "#0f172a",
            "#1e293b",
            "#e2e8f0",
            "#94a3b8",
            "#38bdf8",
            "#0284c7",
            "#334155",
            "#e2e8f0",
            '"Inter", "Segoe UI", Arial, sans-serif',
        ),
        plotly_template="hive_dark_analysis",
        plotly_layout=_plotly_layout(
            paper_bgcolor="#0f172a",
            plot_bgcolor="#111827",
            font_family="Inter, Arial, sans-serif",
            font_color="#e2e8f0",
            colorway=["#38bdf8", "#a78bfa", "#4ade80", "#fbbf24", "#f87171"],
            gridcolor="#334155",
            linecolor="#475569",
            margin={"l": 70, "r": 30, "t": 60, "b": 60},
            legend_bgcolor="rgba(30,41,59,0.90)",
            legend_bordercolor="#334155",
            modebar_color="#94a3b8",
            modebar_activecolor="#38bdf8",
        ),
    ),
}


def get_theme(style_name: str) -> HiveTheme:
    """Return a named theme or raise an informative error for an unknown name."""
    try:
        return THEMES[style_name]
    except KeyError as error:
        available = ", ".join(sorted(THEMES))
        raise ValueError(
            f"Unknown HIVE style {style_name!r}. Available styles: {available}"
        ) from error


def register_plotly_theme(theme: HiveTheme) -> None:
    """Register a theme and make it the default for subsequently created figures."""
    pio.templates[theme.plotly_template] = layout.Template(
        layout=dict(theme.plotly_layout)
    )
    pio.templates.default = theme.plotly_template