<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# As I am using dash plotly as current library to plot my results, I would like you to do a research on which are the customable parameters to be modified for HIVE. I mean all the GUI custom eleemtns like:

Fonts
Button styles
And so on.
Please report on a markdown all the customizable components

Below is a practical inventory of the GUI elements you can customize in HIVE using Dash + Plotly. The key distinction is that **Dash controls the app shell** (fonts, buttons, cards, layout, colors) through CSS/HTML/component properties, while **Plotly controls the figures themselves** (fonts, axes, legends, colors, hover, modebar) through `fig.update_layout()` and trace properties.[^1_1][^1_2]

# HIVE GUI customization report

## Recommended styling architecture

For HIVE, keep all visual settings centralized in a theme module and CSS files, rather than hard-coding colors or fonts inside pages:

```text
frontend/
├── app/
│   └── app.py
├── assets/
│   ├── 00_typography.css
│   ├── 10_theme.css
│   ├── 20_components.css
│   └── favicon.ico
└── theme/
    └── hive_theme.py
```

Dash automatically serves CSS, JavaScript, images, and `favicon.ico` from an `assets/` folder; custom CSS is loaded after Dash component CSS, so it can override defaults.[^1_1]

## Global application theme

| Customizable element | Where to set it | Typical parameters |
| :-- | :-- | :-- |
| App font | `assets/00_typography.css`, `body` | `font-family`, `font-size`, `line-height`, `letter-spacing` |
| Global text color | CSS `body` or CSS variables | `color`, `--hive-text`, `--hive-text-muted` |
| Background colors | CSS variables / component `style` | `--hive-bg`, `--hive-surface`, `--hive-border` |
| Primary accent color | CSS variables / buttons | `--hive-primary`, hover/active variants |
| Dark/light mode | CSS variables + `dcc.Store` or URL parameter | Background, text, borders, chart template |
| Page title | `Dash(title=...)` | Browser-tab title |
| Loading message | `Dash(update_title=...)` | Text shown while callbacks run |
| Favicon | `assets/favicon.ico` | Browser-tab icon |
| Meta tags / viewport | `Dash(meta_tags=...)` | Mobile scaling, description, charset |
| HTML shell | `app.index_string` or `interpolate_index` | Custom header/footer, fonts, external scripts |

Dash lets you set the browser title, callback “Updating…” message, favicon, meta tags, and even the HTML index template.[^1_1]

Example global theme:

```css
:root {
  --hive-bg: #f5f7fa;
  --hive-surface: #ffffff;
  --hive-text: #1f2933;
  --hive-text-muted: #5f6b76;
  --hive-primary: #0b5fff;
  --hive-primary-hover: #094bcc;
  --hive-success: #1f9d55;
  --hive-warning: #d97706;
  --hive-danger: #d64545;
  --hive-border: #d9e2ec;
  --hive-radius: 8px;
  --hive-font: "Inter", "Segoe UI", Arial, sans-serif;
}

body {
  background-color: var(--hive-bg);
  color: var(--hive-text);
  font-family: var(--hive-font);
}
```


## Typography

| Element | CSS selector / Dash property | Customizable parameters |
| :-- | :-- | :-- |
| Body text | `body` | Font family, size, weight, color, line height |
| Page title | `html.H1`, `.hive-page-title` | Size, weight, color, margin, letter spacing |
| Section headings | `html.H2`, `html.H3` | Size, weight, color, uppercase |
| Labels | `html.Label`, `.hive-label` | Size, color, weight, spacing |
| Helper text | `html.Small`, `.hive-help-text` | Size, muted color, italic |
| Code / file paths | `html.Code`, `.hive-code` | Monospace font, background, padding |
| Plot title | Plotly `layout.title.font` | Family, size, color, weight, style, capitalization |
| Axis titles | Plotly `layout.xaxis.title.font` | Family, size, color, weight |
| Tick labels | Plotly `layout.xaxis.tickfont` | Family, size, color |
| Legend text | Plotly `layout.legend.font` | Family, size, color, weight |

Plotly’s global `layout.font` applies to titles and tick labels, and individual elements such as axis titles, legend text, and annotations can override it.[^1_2][^1_3]

## Layout and page structure

| HIVE element | Dash component | Customizable properties |
| :-- | :-- | :-- |
| Main container | `html.Div` | `className`, `style`, width, max-width, padding, margin |
| Sidebar | `html.Aside`, `dbc.Nav` | Width, background, border, collapse behavior |
| Header / top bar | `html.Header`, `html.Div` | Height, background, shadow, logo, alignment |
| Footer | `html.Footer` | Height, background, text color, links |
| Content area | `html.Main`, `dbc.Container` | Padding, max width, responsive columns |
| Cards / panels | `dbc.Card`, `html.Div` | Border, radius, shadow, background, padding |
| Plot area | `dcc.Graph` | `style`, `className`, height, responsive behavior |
| Tabs | `dcc.Tabs`, `dcc.Tab` | Selected/unselected colors, borders, font, height |
| Accordion | `dbc.Accordion`, `dbc.AccordionItem` | Header style, border, background, icon |
| Modal | `dbc.Modal` | Size, backdrop, header/footer, animation |
| Toast / alerts | `dbc.Toast`, `dbc.Alert` | Color, icon, duration, position |
| Spinner | `dcc.Loading`, `dbc.Spinner` | Color, size, type, overlay text |

Dash’s `style` accepts a Python dictionary with camelCase CSS keys, while `className` applies CSS classes defined in the `assets` folder.[^1_4][^1_1]

## Buttons and interactive controls

| Control | Component | Customizable parameters |
| :-- | :-- | :-- |
| Primary / secondary buttons | `dbc.Button`, `html.Button` | Background, text color, border, radius, padding, hover, disabled state |
| Icon buttons | `dbc.Button` + icon library | Icon size, color, padding, tooltip |
| Dropdowns | `dcc.Dropdown` | Placeholder, font, border, background, selected option color, clearable |
| Multi-select | `dcc.Dropdown(multi=True)` | Selected-chip colors, max height, search placeholder |
| Radio buttons | `dcc.RadioItems` | Label style, selected color, inline layout |
| Checkboxes | `dcc.Checklist` | Label style, checked color, spacing |
| Sliders | `dcc.Slider`, `dcc.RangeSlider` | Track color, handle color, tooltip, marks, step |
| Numeric input | `dcc.Input(type="number")` | Width, font, border, validation message |
| Text search | `dcc.Input(type="text")` | Placeholder, icon, focus border, background |
| Date / time | `dcc.DatePickerRange` | Calendar colors, fonts, range highlight |
| Switch / toggle | `dbc.Switch` | Track color, checked color, size |
| Upload button | `dcc.Upload` | Drag area, border, hover, accepted file text |
| Download button | `dcc.Download` | Button style, filename, file format |
| Tooltip | `dbc.Tooltip` | Background, text color, delay, placement |

For a consistent HIVE look, define reusable CSS classes such as `.hive-btn`, `.hive-btn--primary`, `.hive-control`, and `.hive-card`, then apply them through `className`.

Example:

```css
.hive-btn--primary {
  background-color: var(--hive-primary);
  color: white;
  border: none;
  border-radius: var(--hive-radius);
  font-weight: 600;
}

.hive-btn--primary:hover {
  background-color: var(--hive-primary-hover);
}
```


## Plotly figure customization

These parameters should be managed by HIVE’s `PlotStyle` class and applied consistently to every generated figure. The HIVE roadmap already identifies typography, axes, tick settings, line thickness, DPI, and export configuration as central plot-style responsibilities.[^1_5]


| Plot element | Plotly location | Main customizable parameters |
| :-- | :-- | :-- |
| Global font | `layout.font` | `family`, `size`, `color`, `weight`, `style` |
| Figure title | `layout.title` | Text, font, position, alignment, padding, subtitle |
| Figure background | `layout.paper_bgcolor` | Outer figure background |
| Plot background | `layout.plot_bgcolor` | Background inside axes |
| Margins | `layout.margin` | `l`, `r`, `t`, `b`, `pad` |
| Figure size | `layout.width`, `layout.height` | Fixed pixel dimensions; use `autosize` for responsive plots |
| Axis title | `layout.xaxis.title` / `layout.yaxis.title` | Text, font, standoff |
| Axis range | `layout.xaxis.range` | Minimum, maximum, autorange |
| Axis type | `layout.xaxis.type` | `linear`, `log`, `date`, `category` |
| Grid lines | `layout.xaxis.gridcolor`, `gridwidth` | Visibility, color, thickness, dash style |
| Zero line | `layout.xaxis.zeroline` | Color, width |
| Ticks | `layout.xaxis.tickfont`, `tickformat`, `dtick` | Font, format, spacing, rotation, angle |
| Line color cycle | `layout.colorway` | Ordered list of trace colors |
| Continuous colormap | `layout.coloraxis.colorscale` or trace `colorscale` | Sequential, diverging, custom scale |
| Trace line | `trace.line` | Color, width, dash, shape |
| Markers | `trace.marker` | Symbol, size, color, opacity, border |
| Fill / area | `trace.fill`, `fillcolor` | Fill color, opacity |
| Legend | `layout.legend` | Position, orientation, background, border, font, item order |
| Hover labels | `layout.hoverlabel`, `trace.hovertemplate` | Background, font, border, custom text |
| Hover behavior | `layout.hovermode` | `closest`, `x`, `y`, `x unified`, `y unified` |
| Modebar | `layout.modebar` | Background, icon color, active color, orientation, added/removed buttons |
| Colorbar | `layout.coloraxis.colorbar` | Length, thickness, title, tick font, position |
| Annotations | `layout.annotations` | Text, font, position, arrow, background |
| Shapes | `layout.shapes` | Lines, rectangles, thresholds, injury-criterion limits |
| Templates | `layout.template` | Reusable global Plotly theme |

Plotly supports a global font through `layout.font`; fonts in traces and other layout components inherit it unless specifically overridden. It also provides `paper_bgcolor`, `plot_bgcolor`, colorways, default color scales, legend styling, hover modes, and modebar styling.[^1_2]

Example HIVE scientific plot theme:

```python
import plotly.graph_objects as go

HIVE_LAYOUT = dict(
    template="plotly_white",
    font=dict(
        family="Inter, Segoe UI, Arial, sans-serif",
        size=13,
        color="#1f2933",
    ),
    title=dict(
        font=dict(size=17, weight=700),
        x=0.01,
        xanchor="left",
    ),
    margin=dict(l=70, r=30, t=60, b=60),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    colorway=[
        "#0b5fff", "#d97706", "#1f9d55",
        "#d64545", "#7c3aed", "#0891b2",
    ],
    legend=dict(
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#d9e2ec",
        borderwidth=1,
    ),
    hovermode="x unified",
)

fig = go.Figure()
fig.update_layout(**HIVE_LAYOUT)
```


## Plotly modebar

The modebar is the small toolbar displayed on a `dcc.Graph`. It can be styled and its buttons can be added or removed.[^1_2]


| Element | Parameter | Options |
| :-- | :-- | :-- |
| Background | `modebar.bgcolor` | Any CSS color |
| Icon color | `modebar.color` | Any CSS color |
| Active/hover icon | `modebar.activecolor` | Any CSS color |
| Orientation | `modebar.orientation` | `h` or `v` |
| Add buttons | `modebar.add` | Zoom, pan, lasso, spike lines, image download, etc. |
| Remove buttons | `modebar.remove` | Zoom, autoscale, select, `toImage`, etc. |
| Graph config | `dcc.Graph(config=...)` | `displayModeBar`, `responsive`, `toImageButtonOptions`, `scrollZoom`, `doubleClick` |

For HIVE, a useful default is to keep zoom, pan, reset, and SVG/PNG export while removing unnecessary 3D or cloud-related controls.

```python
dcc.Graph(
    figure=fig,
    config={
        "displayModeBar": True,
        "responsive": True,
        "scrollZoom": True,
        "toImageButtonOptions": {
            "format": "svg",
            "filename": "hive_plot",
            "scale": 2,
        },
    },
)
```


## Data tables and metadata panels

| Element | Component | Customizable parameters |
| :-- | :-- | :-- |
| Table container | `dash_table.DataTable` or `dbc.Table` | Border, row height, zebra striping, font |
| Header row | CSS / table properties | Background, text color, font weight, sticky behavior |
| Cells | CSS / table properties | Padding, alignment, number formatting |
| Selected rows | `selected_rows`, CSS | Highlight color, border |
| Sortable columns | `sort_action` | Sort icons, header cursor |
| Filterable columns | `filter_action` | Input style, placeholder |
| Conditional formatting | `style_data_conditional` | Color scales, thresholds, bold values |
| Metadata cards | `dbc.Card`, `html.Dl` | Label/value typography, icon, spacing |

For HIVE, conditional formatting is particularly useful for injury criteria, energy-balance errors, simulation status, or case-validation warnings.

## Animation and time controls

| Element | Component | Customizable parameters |
| :-- | :-- | :-- |
| Animation slider | `dcc.Slider` | Handle, track, marks, tooltip, step |
| Play / pause | `dbc.Button` or `dcc.Interval` | Icon, color, disabled state |
| Playback speed | `dcc.Dropdown` or `dcc.RadioItems` | Options, selected style |
| Current time label | `html.Div` | Font, color, monospace formatting |
| Animation frame | Plotly frames / `dcc.Interval` | Duration, transition, redraw behavior |
| Component visibility | `dcc.Checklist` | Which body parts, curves, or criteria are shown |

The HIVE roadmap includes an `AnimationStyle` concept for animated or component-based visualization settings, so these controls should be part of the frontend theme as well.[^1_5]

## Export and publication settings

| Element | Where | Customizable parameters |
| :-- | :-- | :-- |
| Export format | `dcc.Download`, Plotly config | SVG, PNG, PDF, CSV |
| Export resolution | Plotly `toImageButtonOptions.scale` | Pixel multiplier |
| Export filename | `toImageButtonOptions.filename` | Default filename |
| Figure size on export | `layout.width`, `layout.height` | Width and height in px |
| Font embedding | Plotly layout font | Font family available in the browser/system |
| Background transparency | `paper_bgcolor`, `plot_bgcolor` | `rgba(0,0,0,0)` for transparent export |
| CSV export | `dcc.Download` | Delimiter, decimal separator, column names |

Plotly supports customizing the modebar image-export options, including format, filename, and scale.[^1_1][^1_2]

## Suggested HIVE theme parameters

A compact `hive_theme.py` could expose these groups:

```python
@dataclass(frozen=True)
class HiveTheme:
    # App
    font_family: str = "Inter, Segoe UI, Arial, sans-serif"
    font_size: int = 14
    background: str = "#f5f7fa"
    surface: str = "#ffffff"
    text: str = "#1f2933"
    text_muted: str = "#5f6b76"
    border: str = "#d9e2ec"

    # Brand
    primary: str = "#0b5fff"
    primary_hover: str = "#094bcc"
    success: str = "#1f9d55"
    warning: str = "#d97706"
    danger: str = "#d64545"

    # Layout
    radius: str = "8px"
    card_padding: str = "16px"
    sidebar_width: str = "280px"

    # Plotly
    plot_template: str = "plotly_white"
    plot_font_size: int = 13
    plot_title_size: int = 17
    colorway: tuple = (
        "#0b5fff", "#d97706", "#1f9d55",
        "#d64545", "#7c3aed", "#0891b2",
    )
    hovermode: str = "x unified"
```

This aligns well with HIVE’s intended separation between generic core infrastructure and case-specific modules: the theme belongs in the core/frontend layer, while individual whiplash, airbag, or energy-balance modules should only provide data-specific plots and criteria.[^1_5]

## Priority customization list for HIVE

1. **CSS variables**: colors, fonts, radius, borders, shadows.
2. **Reusable component classes**: buttons, cards, sidebar, headers, form controls.
3. **Plotly template**: global font, background, colorway, margins, legend, hover.
4. **Axis style**: titles, tick fonts, gridlines, zero lines, number/date formats.
5. **Modebar and export**: visible buttons, SVG export, filename, scale.
6. **Dark mode**: a parallel set of CSS variables plus a Plotly dark template.
7. **Status colors**: success, warning, danger, and info for simulation validation and criteria thresholds.
8. **Responsive rules**: sidebar collapse, card stacking, plot resizing, mobile-friendly controls.

Dash’s `assets` mechanism is the cleanest place to implement most of these customizations, because it automatically loads local CSS and supports hot reloading during development.[^1_1]

<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://dash.plotly.com/external-resources

[^1_2]: https://plotly.com/python/reference/layout/

[^1_3]: https://plotly.com/python/figure-labels/

[^1_4]: https://www.scribd.com/document/637758784/Part-1-Layout-Dash-for-Python-Documentation-Plotly

[^1_5]: HIVE_roadmap - stage 1.0.md

[^1_6]: https://dash.plotly.com/

[^1_7]: https://docs.plotly.com/

[^1_8]: https://community.plotly.com/t/how-to-partially-update-classname/71665

[^1_9]: https://www.scribd.com/document/424146566/Dash-User-Guide-and-Documentation

[^1_10]: https://deepwiki.com/plotly/plotly.py/4.4-styling-and-theming

[^1_11]: https://deepwiki.com/plotly/plotly.py/4.2-layout-configuration

[^1_12]: https://pytutorial.com/plotly-update-layout-customize-figure-appearance/

[^1_13]: https://sqlpad.io/courses/plotly/layout-and-styling-in-plotly/colors-font-and-other-styling-options/

[^1_14]: https://stackoverflow.com/questions/63394603/plotly-dash-linking-external-local-css

[^1_15]: https://community.plotly.com/t/object-oriented-dash-components/10809

[^1_16]: https://community.plotly.com/t/how-to-work-with-custom-css-file-in-dash-app/80650


---

# Starting from this prerogatives, please see the following websites:

[HBM Safety Suite | Autoliv](https://www.autoliv.com/safety-solutions/hbm-safety-suite)
[HBM Connect® | Humanetics](https://www.humaneticsgroup.com/products/virtual-models/hbm-connect)
[Metriks™ — No-Code Injury Metrics Post-Processor](https://www.elemance.com/metriks/)
[Welcome to Volvo](https://www.volvo.com/en/)
These websites will be as inspiration for 5 proposal of customized dash and plotly designs.
Try to average this 4 website and propose 5 configurations to be used for HIVE.
Report in a Markdown to provide to my agent that will then implement in the repository one of the five styles

Below is a ready-to-hand-off Markdown specification with **five HIVE design proposals**. They synthesize the engineering-oriented, clean, safety-focused visual language of Autoliv’s HBM Safety Suite, Humanetics HBM Connect, Elemance Metriks, and Volvo’s restrained Scandinavian/product-brand aesthetic.[^2_1][^2_2][^2_3][^2_4]

# HIVE GUI Design Proposals

## Design intent

HIVE should look like a professional engineering and scientific post-processing environment: calm, data-dense, readable, and suitable for both interactive exploration and publication-quality output. The references emphasize human-body-model workflows, injury-metric assessment, risk visualization, batch analysis, and repeatable reporting; HIVE should translate these ideas into a clean Dash/Plotly interface rather than a marketing-style website.[^2_2][^2_3][^2_1]

The common visual direction should be:

- Light neutral background with high-contrast data areas.
- One restrained primary accent color, plus semantic status colors.
- Clear typographic hierarchy and generous spacing.
- Compact but legible controls for simulation, case, part, and criterion selection.
- Scientific Plotly styling: white plot backgrounds, subtle grids, unified hover, and SVG export.
- Optional dark mode for long analysis sessions.


## Shared HIVE design system

All five proposals should use the same component architecture and differ mainly in color, density, and visual character.

### Recommended folder structure

```text
frontend/
├── app/
│   └── app.py
├── assets/
│   ├── 00_typography.css
│   ├── 10_theme.css
│   ├── 20_layout.css
│   ├── 30_components.css
│   ├── 40_plots.css
│   └── favicon.ico
└── theme/
    ├── hive_theme.py
    ├── plot_templates.py
    └── palettes.py
```

Dash automatically loads CSS from the `assets` folder, and custom CSS can override Dash component defaults.[^2_5]

### Core CSS variables

```css
:root {
  /* Typography */
  --hive-font: "Inter", "Segoe UI", Arial, sans-serif;
  --hive-font-mono: "JetBrains Mono", "Consolas", monospace;

  /* Surfaces */
  --hive-bg: #f4f6f8;
  --hive-surface: #ffffff;
  --hive-surface-alt: #eef2f5;
  --hive-border: #d9e2ec;

  /* Text */
  --hive-text: #17222b;
  --hive-text-muted: #5f6b76;

  /* Brand */
  --hive-primary: #0b5fff;
  --hive-primary-hover: #094bcc;
  --hive-accent: #00a3a3;

  /* Status */
  --hive-success: #1f9d55;
  --hive-warning: #d97706;
  --hive-danger: #d64545;
  --hive-info: #0b5fff;

  /* Shape */
  --hive-radius-sm: 6px;
  --hive-radius: 10px;
  --hive-radius-lg: 16px;
  --hive-shadow: 0 2px 8px rgba(23, 34, 43, 0.08);
}
```


### Core Plotly template

```python
HIVE_PLOT_TEMPLATE = dict(
    template="plotly_white",
    font=dict(
        family="Inter, Segoe UI, Arial, sans-serif",
        size=13,
        color="#17222b",
    ),
    margin=dict(l=70, r=30, t=60, b=60),
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    colorway=[
        "#0b5fff", "#00a3a3", "#d97706",
        "#d64545", "#7c3aed", "#0891b2",
    ],
    legend=dict(
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#d9e2ec",
        borderwidth=1,
    ),
    hovermode="x unified",
)
```

Plotly’s `layout` object controls figure-wide typography, backgrounds, margins, color sequences, legend behavior, hover mode, and other visual properties.[^2_6]

______________________________________________________________________

# Proposal 1 — HIVE Clinical

**Best for:** scientific publication, injury-criteria review, clean comparison of simulations.

### Visual character

A light, clinical, highly readable interface inspired by the restrained product presentation of Autoliv and Humanetics. It should feel trustworthy, calm, and focused on numerical results.[^2_1][^2_2]

### Color palette

| Role | Color |
| :-- | :-- |
| Background | `#f7f9fb` |
| Card surface | `#ffffff` |
| Primary | `#0057b8` |
| Secondary accent | `#00a3a3` |
| Text | `#17222b` |
| Muted text | `#5f6b76` |
| Success | `#1f9d55` |
| Warning | `#d97706` |
| Danger | `#d64545` |

### Typography

| Element | Style |
| :-- | :-- |
| App title | Inter, 20–22 px, weight 700 |
| Section title | Inter, 16–18 px, weight 600 |
| Body / labels | Inter, 13–14 px, weight 400 |
| Numeric values | JetBrains Mono or Consolas, 13 px |
| Plot title | Inter, 16–18 px, weight 600 |
| Axis labels | Inter, 12–13 px |

### Layout

```text
┌──────────────────────────────────────────────┐
│ HIVE | Whiplash Analysis          [Dark mode]│
├──────────────┬───────────────────────────────┤
│ Simulation   │  Overview cards               │
│ selector     │  ┌─────┐ ┌─────┐ ┌─────┐      │
│              │  │Nij  │ │NIC  │ │Sa   │      │
│ Case         │  └─────┘ └─────┘ └─────┘      │
│ selector     │                               │
│              │  Main comparison plot          │
│ Body region  │                               │
│ selector     │  Secondary plots / table       │
└──────────────┴───────────────────────────────┘
```


### Dash components

- `dbc.Container` with a fixed 280–320 px sidebar.
- `dbc.Card` panels for criteria, metadata, and plot controls.
- `dcc.Dropdown` for simulations, cases, parts, and channels.
- `dcc.RangeSlider` for time-window selection.
- `dcc.Graph` for comparison plots.
- `dbc.Alert` for validation and threshold warnings.
- `dcc.Download` for SVG/PNG/CSV export.


### Plotly styling

- White plot background.
- Light gray gridlines: `#e5eaef`.
- Thin colored reference lines for injury thresholds.
- Unified hover on the x-axis.
- Conservative color cycle with blue as the primary simulation color.
- SVG export enabled by default.


### Recommended use

Use this as HIVE’s default design. It is the safest option for a research tool because it prioritizes legibility, consistency, and scientific credibility.

______________________________________________________________________

# Proposal 2 — HIVE Engineering Console

**Best for:** daily simulation analysis, dense multi-case comparison, power users.

### Visual character

A compact, technical console inspired by engineering software and Metriks’ emphasis on automated, repeatable post-processing. It should maximize visible information without becoming visually noisy.[^2_3]

### Color palette

| Role | Color |
| :-- | :-- |
| Background | `#eef1f4` |
| Panel surface | `#ffffff` |
| Sidebar | `#1f2933` |
| Primary | `#2563eb` |
| Accent | `#f59e0b` |
| Text | `#111827` |
| Muted text | `#6b7280` |
| Success | `#16a34a` |
| Warning | `#d97706` |
| Danger | `#dc2626` |

### Typography

| Element | Style |
| :-- | :-- |
| App title | Inter, 18 px, uppercase, letter-spacing 0.04 em |
| Sidebar labels | Inter, 12 px, uppercase |
| Data values | JetBrains Mono, 12–13 px |
| Plot titles | Inter, 15–16 px, weight 600 |
| Axis labels | Inter, 12 px |

### Layout

```text
┌──────────────────────────────────────────────────────┐
│ HIVE ENGINEERING CONSOLE | Case: Whiplash            │
├───────────┬──────────────────────────────────────────┤
│ SIMULATIONS│  Filter bar: case | region | metric      │
│ CASES      │  ┌────────────┐ ┌────────────┐           │
│ PARTS      │  │ Criterion  │ │ Status     │           │
│ CHANNELS   │  └────────────┘ └────────────┘           │
│            │  ┌────────────┐ ┌────────────┐           │
│ Time range │  │ Plot 1     │ │ Plot 2     │           │
│ Plot type  │  └────────────┘ └────────────┘           │
│ Export     │  ┌──────────────────────────┐            │
│            │  │ Data table / metadata     │            │
└───────────┴──────────────────────────────────────────┘
```


### Dash components

- Dark sidebar with `dbc.Nav`.
- Dense `dbc.Card` grid, 2–3 columns.
- `dcc.Dropdown(multi=True)` for simulation comparison.
- `dcc.Checklist` for body regions and output channels.
- `dcc.Slider` for animation/time control.
- `dash_table.DataTable` for criterion values and thresholds.
- `dbc.Tooltip` for parameter explanations.


### Plotly styling

- Compact margins: `l=55, r=20, t=45, b=45`.
- Smaller fonts: 11–12 px for ticks, 12–13 px for titles.
- Multiple small plots rather than one large plot.
- Color-coded simulation runs.
- Dashed threshold lines and shaded risk regions.
- Modebar visible with zoom, pan, reset, and SVG export.


### Recommended use

Use this for the main HIVE analysis workspace, especially when users compare many LS-DYNA cases, parts, and derived metrics simultaneously.

______________________________________________________________________

# Proposal 3 — HIVE Safety Assessment

**Best for:** injury-risk interpretation, threshold visualization, case validation.

### Visual character

A more assessment-oriented design inspired by Metriks’ focus on injury metrics, risk visualization, and region-based assessment across head, neck, thorax, abdomen, and lower extremities.[^2_3]

### Color palette

| Role | Color |
| :-- | :-- |
| Background | `#f6f8fa` |
| Card surface | `#ffffff` |
| Primary | `#0f766e` |
| Neutral accent | `#334155` |
| Low risk | `#1f9d55` |
| Moderate risk | `#d97706` |
| High risk | `#d64545` |
| Text | `#17222b` |
| Muted text | `#5f6b76` |

### Typography

| Element | Style |
| :-- | :-- |
| App title | Inter, 20 px, weight 700 |
| Criterion name | Inter, 15 px, weight 600 |
| Risk value | JetBrains Mono, 18–22 px, weight 700 |
| Status label | Inter, 12 px, uppercase |
| Plot labels | Inter, 12–13 px |

### Layout

```text
┌──────────────────────────────────────────────────────┐
│ HIVE SAFETY ASSESSMENT                                │
├──────────────┬───────────────────────────────────────┤
│ Case         │  Risk summary                         │
│ Simulation   │  Head | Neck | Thorax | PLEX          │
│ Body region  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│              │  │ Low  │ │ Mod. │ │ High │ │ Low  │  │
│ Criteria     │  └──────┘ └──────┘ └──────┘ └──────┘  │
│              │                                       │
│              │  Criterion time histories              │
│              │  Threshold / risk curves               │
│              │  Detailed table and export             │
└──────────────┴───────────────────────────────────────┘
```


### Dash components

- `dbc.Card` summary tiles for each body region.
- `dbc.Badge` for risk classification: low, moderate, high.
- `dcc.Dropdown` for criterion selection.
- `dcc.Graph` with reference curves and shaded risk bands.
- `dbc.Progress` or `dbc.Progress` bar for normalized criterion values.
- `dbc.Alert` for threshold exceedance.
- `dcc.Download` for assessment report and plots.


### Plotly styling

- Use green, amber, and red only for risk meaning, not decoration.
- Add horizontal threshold lines with labels.
- Shade acceptable, caution, and exceedance regions.
- Use `hovermode="x unified"` for synchronized time-history inspection.
- Use a muted scientific color cycle for simulation curves.
- Use annotations to mark peak values and threshold crossings.


### Recommended use

Use this when HIVE is used for injury-criteria evaluation and decision support. It should make threshold exceedance immediately visible without exaggerating uncertainty.

______________________________________________________________________

# Proposal 4 — HIVE Scandinavian Minimal

**Best for:** presentations, external stakeholders, clean demonstration version of HIVE.

### Visual character

A minimal Scandinavian-inspired design inspired by Volvo’s restrained, spacious, and product-focused presentation. It should use whitespace, simple geometry, and a small number of strong accents.[^2_4]

### Color palette

| Role | Color |
| :-- | :-- |
| Background | `#fafafa` |
| Card surface | `#ffffff` |
| Primary | `#003057` |
| Secondary | `#707070` |
| Accent | `#006d77` |
| Text | `#141414` |
| Muted text | `#6b6b6b` |
| Border | `#e0e0e0` |

### Typography

| Element | Style |
| :-- | :-- |
| App title | Inter, 22 px, weight 600 |
| Section titles | Inter, 16 px, weight 500 |
| Body text | Inter, 14 px, weight 400 |
| Numeric values | Inter, 14–16 px, weight 500 |
| Plot labels | Inter, 12–13 px |

### Layout

```text
┌──────────────────────────────────────────────┐
│ HIVE                                          │
│                                               │
│  Simulation overview                          │
│  ┌───────────────┐  ┌───────────────┐         │
│  │ Selected case │  │ Key metrics   │         │
│  └───────────────┘  └───────────────┘         │
│                                               │
│  Main visualization                           │
│  ┌───────────────────────────────────────┐    │
│  │ Large plot                             │    │
│  └───────────────────────────────────────┘    │
│                                               │
│  Controls: minimal, bottom or right-aligned   │
└──────────────────────────────────────────────┘
```


### Dash components

- Large `dbc.Container` with generous padding.
- Minimal sidebar or top navigation.
- `dbc.Card` with no heavy borders, only subtle shadow.
- `dbc.Button` with rounded corners and restrained color.
- `dcc.Dropdown` styled with minimal borders.
- One large `dcc.Graph` per view.
- `dbc.Modal` for advanced settings.


### Plotly styling

- Very clean `plotly_white` template.
- No gridlines by default, or only very light horizontal gridlines.
- Large margins and generous spacing.
- One or two colors per plot.
- Minimal legend, placed below or outside the plot.
- Large, clear axis titles.
- SVG export with a transparent background option.


### Recommended use

Use this for demos, project meetings, and public-facing screenshots. It is elegant but less efficient for dense engineering work.

______________________________________________________________________

# Proposal 5 — HIVE Dark Analysis

**Best for:** long working sessions, HPC result inspection, modern technical dashboard.

### Visual character

A dark technical dashboard with high-contrast plots and clear status colors. It should feel modern and focused, while retaining scientific readability.

### Color palette

| Role | Color |
| :-- | :-- |
| Background | `#0f172a` |
| Panel surface | `#1e293b` |
| Sidebar | `#111827` |
| Border | `#334155` |
| Primary | `#38bdf8` |
| Accent | `#a78bfa` |
| Text | `#e2e8f0` |
| Muted text | `#94a3b8` |
| Success | `#4ade80` |
| Warning | `#fbbf24` |
| Danger | `#f87171` |

### Typography

| Element | Style |
| :-- | :-- |
| App title | Inter, 20 px, weight 700 |
| Sidebar labels | Inter, 12 px, uppercase |
| Body text | Inter, 13–14 px |
| Numeric values | JetBrains Mono, 13 px |
| Plot titles | Inter, 15–17 px, weight 600 |
| Axis labels | Inter, 12 px |

### Layout

```text
┌──────────────────────────────────────────────┐
│ HIVE DARK ANALYSIS                            │
├───────────┬──────────────────────────────────┤
│ Simulations│  Metric cards                    │
│ Cases      │  ┌──────┐ ┌──────┐ ┌──────┐      │
│ Parts      │  └──────┘ └──────┘ └──────┘      │
│ Channels   │                                  │
│            │  Main plot                        │
│ Time       │                                  │
│ Export     │  Comparison plots                 │
└───────────┴──────────────────────────────────┘
```


### Dash components

- Dark `dbc.Card` surfaces.
- `dbc.Switch` or `dbc.Button` for light/dark mode.
- `dcc.Dropdown` with dark background and light text.
- `dcc.Graph` using a dark Plotly template.
- `dbc.Alert` with translucent colored backgrounds.
- `dcc.Loading` with a light spinner.
- `dcc.Download` for SVG/PNG export.


### Plotly styling

- `paper_bgcolor="#0f172a"`.
- `plot_bgcolor="#111827"`.
- Light gray or translucent gridlines.
- Bright but non-neon data colors.
- Light-colored axis text and titles.
- High-contrast hover labels.
- SVG export with a white or transparent background for reports.


### Recommended use

Use this as an optional HIVE theme, activated from the interface. It is especially useful for extended analysis sessions but should not be the only available theme because printed reports and bright environments favor light themes.

______________________________________________________________________

# Implementation guidance for the agent

## Theme selection

Implement the five proposals as selectable themes, with **HIVE Clinical** as the default.

```python
HIVE_THEMES = {
    "clinical": "HIVE Clinical",
    "engineering_console": "HIVE Engineering Console",
    "safety_assessment": "HIVE Safety Assessment",
    "scandinavian_minimal": "HIVE Scandinavian Minimal",
    "dark_analysis": "HIVE Dark Analysis",
}
```

The selected theme should update:

1. CSS variables through a `dcc.Store`, callback, or dynamically loaded stylesheet.
2. The Plotly template used by all figures.
3. Button, card, sidebar, dropdown, and table styling.
4. Plot background, gridline, text, and colorway settings.
5. Export defaults.

## Required reusable CSS classes

```css
.hive-app {}
.hive-sidebar {}
.hive-header {}
.hive-main {}
.hive-card {}
.hive-card-title {}
.hive-metric-card {}
.hive-label {}
.hive-help-text {}
.hive-btn {}
.hive-btn--primary {}
.hive-btn--secondary {}
.hive-btn--danger {}
.hive-control {}
.hive-plot-container {}
.hive-table {}
.hive-badge--success {}
.hive-badge--warning {}
.hive-badge--danger {}
```


## Required Plotly functions

Implement centralized helpers rather than styling each figure independently:

```python
def apply_hive_theme(fig, theme="clinical"):
    ...

def style_time_history(fig, theme="clinical"):
    ...

def add_threshold(fig, y, label, level="warning", theme="clinical"):
    ...

def style_comparison_plot(fig, simulations, theme="clinical"):
    ...

def configure_export(fig, filename="hive_plot", fmt="svg"):
    ...
```


## Minimum acceptance criteria

The implemented theme should:

- Use CSS variables for all recurring colors and fonts.
- Avoid hard-coded colors inside individual Dash pages.
- Apply one consistent Plotly template across all plots.
- Preserve readable contrast for text, axes, gridlines, and hover labels.
- Support light and dark modes, or at least be structured to add dark mode later.
- Provide SVG export from the Plotly modebar.
- Keep simulation curves, thresholds, annotations, and risk bands visually distinguishable.
- Work with HIVE’s modular case structure, so whiplash, airbag, and energy-balance modules inherit the same visual system.[^2_7]


## Recommended default

Implement **Proposal 1 — HIVE Clinical** first. It offers the best balance between the scientific rigor expected from an LS-DYNA post-processing tool, the clean product-oriented presentation seen in Autoliv and Humanetics materials, and the practical injury-assessment focus of Metriks.[^2_2][^2_1][^2_3]

<div align="center">⁂</div>

[^2_1]: https://www.autoliv.com/safety-solutions/hbm-safety-suite

[^2_2]: https://www.humaneticsgroup.com/products/virtual-models/hbm-connect

[^2_3]: https://www.elemance.com/metriks/

[^2_4]: https://www.volvo.com/en/

[^2_5]: https://dash.plotly.com/external-resources

[^2_6]: https://plotly.com/python/reference/layout/

[^2_7]: HIVE_roadmap - stage 1.0.md

