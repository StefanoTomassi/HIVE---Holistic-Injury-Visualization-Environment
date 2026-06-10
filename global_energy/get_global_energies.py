from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from core.io.select_folder import choose_file
from typing import Optional
from core.dataclasses import simulation_dataclasses
SEPARATOR = ";"
HEADER_ROWS = 4  # detected in the file
RELATIVE_THRESHOLD = 0.01
#PlotSettings
PlotSettings = simulation_dataclasses.PlotStyle(
    font_family="sans-serif",
    font_sans_serif="Century Gothic",
    font_size=11,
    axes_spines_top=False,
    axes_spines_right=False,
    axes_linewidth=1.0,
    xtick_major_size=5.0,
    ytick_major_size=5.0,
    xtick_major_width=1.0,
    ytick_major_width=1.0,
    xtick_direction="in",
    ytick_direction="in",
    pdf_fonttype=42,  # TrueType
    ps_fonttype=42,   # TrueType
    svg_fonttype="none",  # Don't convert text to paths in SVG
    savefig_dpi=300
)
def build_signal_metadata(csv_path: Path, sep: str = SEPARATOR, header_rows: int = HEADER_ROWS):
    header = pd.read_csv(csv_path, sep=sep, header=None, nrows=header_rows, dtype=str)
    header = header.fillna("")
    metadata = []

    for col in range(header.shape[1]):
        parts = [str(header.iloc[row, col]).strip() for row in range(header_rows)]
        metadata.append({
            "group": parts[0],
            "quantity": parts[1],
            "variable": parts[2],
            "unit": parts[3],
        })

    return metadata


def load_data(csv_path: Path, sep: str = SEPARATOR, skiprows: int = HEADER_ROWS):
    return pd.read_csv(csv_path, sep=sep, skiprows=skiprows)


def pair_time_value_columns(metadata):
    pairs = []
    i = 0

    while i < len(metadata) - 1:
        left = metadata[i]
        right = metadata[i + 1]

        if "time" in left["variable"].lower():
            pairs.append((i, i + 1, left, right))
            i += 2
        else:
            i += 1

    return pairs


def is_energy_ratio(meta: dict) -> bool:
    quantity = meta["quantity"].lower()
    variable = meta["variable"].lower()
    return "energy ratio" in quantity or "energy_ratio" in variable


def is_total_energy(meta: dict) -> bool:
    quantity = meta["quantity"].lower()
    variable = meta["variable"].lower()
    return "total energy" in quantity or "total_energy" in variable


def get_last_valid_value(series: pd.Series):
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        return float("nan")
    return cleaned.iloc[-1]


def make_legend_label(meta: dict, final_percent: Optional[float] = None) -> str:
    parts = []
    if is_energy_ratio(meta):
        if meta["quantity"]:
            parts.append(meta["quantity"])
        return " | ".join(parts)
    
    if meta["quantity"]:
        parts.append(meta["quantity"])
    if final_percent is not None:
        parts.append(f"final = {final_percent:.2f}% of total")
    return " | ".join(parts)
    
    


def build_energy_percentage_table(df: pd.DataFrame, pairs):
    total_pair = None
    ratio_pair = None

    for pair in pairs:
        value_meta = pair[3]
        if is_total_energy(value_meta):
            total_pair = pair
        elif is_energy_ratio(value_meta):
            ratio_pair = pair

    if total_pair is None:
        raise ValueError("Total energy column not found in the CSV header metadata.")

    total_final = get_last_valid_value(df.iloc[:, total_pair[1]])
    records = []

    for time_idx, value_idx, time_meta, value_meta in pairs:
        y = pd.to_numeric(df.iloc[:, value_idx], errors="coerce")
        final_value = get_last_valid_value(y)
        max_abs_value = y.abs().max()

        if pd.isna(total_final) or total_final == 0:
            final_percent = float("nan")
        else:
            final_percent = 100.0 * final_value / total_final

        records.append({
            "quantity": value_meta["quantity"],
            "variable": value_meta["variable"],
            "unit": value_meta["unit"],
            "final_value": final_value,
            "max_abs_value": max_abs_value,
            "final_percent_of_total": final_percent,
            "is_energy_ratio": is_energy_ratio(value_meta),
            "is_total_energy": is_total_energy(value_meta),
        })

    return pd.DataFrame(records), total_pair, ratio_pair


def plot_global_energy_timeseries(
    csv_path,
    relative_threshold: float = RELATIVE_THRESHOLD,
):
    plt.rcParams.update({
        "font.family": PlotSettings.font_family,
        "font.sans-serif": [PlotSettings.font_sans_serif],
        "font.size": PlotSettings.font_size,
        "axes.spines.top": PlotSettings.axes_spines_top,
        "axes.spines.right": PlotSettings.axes_spines_right,
        "axes.linewidth": PlotSettings.axes_linewidth,
        "xtick.major.size": PlotSettings.xtick_major_size,
        "ytick.major.size": PlotSettings.ytick_major_size,
        "xtick.major.width": PlotSettings.xtick_major_width,
        "ytick.major.width": PlotSettings.ytick_major_width,
        "xtick.direction": PlotSettings.xtick_direction,
        "ytick.direction": PlotSettings.ytick_direction,
        "pdf.fonttype": PlotSettings.pdf_fonttype,
        "ps.fonttype": PlotSettings.ps_fonttype,
        "svg.fonttype": PlotSettings.svg_fonttype,
        "savefig.dpi": PlotSettings.savefig_dpi,
    })

    metadata = build_signal_metadata(csv_path)
    df = load_data(csv_path)
    pairs = pair_time_value_columns(metadata)

    summary_df, total_pair, ratio_pair = build_energy_percentage_table(df, pairs)

    total_energy_series = pd.to_numeric(df.iloc[:, total_pair[1]], errors="coerce")
    total_energy_max = total_energy_series.abs().max()
    threshold_value = relative_threshold * total_energy_max

    fig, (ax_energy, ax_ratio) = plt.subplots(
        2,
        1,
        figsize=(12, 10),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )

    for time_idx, value_idx, time_meta, value_meta in pairs:
        x = pd.to_numeric(df.iloc[:, time_idx], errors="coerce")
        y = pd.to_numeric(df.iloc[:, value_idx], errors="coerce")
        signal_max = y.abs().max()

        row = summary_df.loc[summary_df["variable"] == value_meta["variable"]].iloc[0]
        final_percent = row["final_percent_of_total"]

        if is_energy_ratio(value_meta):
            ax_ratio.plot(
                x,
                y,
                linewidth=1.5,
                label=make_legend_label(value_meta, final_percent=final_percent),
            )
            continue

        if pd.isna(signal_max) or signal_max < threshold_value:
            continue

        label = make_legend_label(value_meta, final_percent=final_percent)
        ax_energy.plot(x, y, linewidth=1.5, label=label)

    time_label = f"{metadata[0]['variable']}"

    energy_unit = ""
    if total_pair is not None:
        energy_unit = summary_df.loc[
            summary_df["variable"] == total_pair[3]["variable"], "unit"
        ].iloc[0]

    ax_energy.set_ylabel(f"Energy [J]".strip())
    ax_energy.set_title(
        f"Global energies (signals above {relative_threshold:.0%} of total energy max)"
    )
    ax_energy.grid(True, linestyle="--", alpha=0.4, linewidth=0.8)
    ax_energy.legend(loc="best", fontsize=0.9 * PlotSettings.font_size, frameon=False)

    if ratio_pair is not None:
        ratio_meta = ratio_pair[3]
        ratio_ylabel = ratio_meta["quantity"]

        ax_ratio.set_title(ratio_meta["quantity"])
        ax_ratio.set_ylabel(ratio_ylabel)
        ax_ratio.grid(True, linestyle="--", alpha=0.4, linewidth=0.8)
        ax_ratio.legend(loc="best", fontsize=0.9 * PlotSettings.font_size, frameon=False)

    ax_ratio.set_xlabel(time_label)

    for ax in (ax_energy, ax_ratio):
        ax.tick_params(
            axis="x",
            direction=PlotSettings.xtick_direction,
            width=PlotSettings.xtick_major_width,
            length=PlotSettings.xtick_major_size,
        )
        ax.tick_params(
            axis="y",
            direction=PlotSettings.ytick_direction,
            width=PlotSettings.ytick_major_width,
            length=PlotSettings.ytick_major_size,
        )

        for spine in ax.spines.values():
            spine.set_linewidth(PlotSettings.axes_linewidth)

    fig.tight_layout()

    percentage_table = summary_df.loc[
        ~summary_df["is_energy_ratio"],
        ["quantity", "final_value", "final_percent_of_total", "max_abs_value"]
    ].copy()

    percentage_table = percentage_table.sort_values(
        "final_percent_of_total",
        ascending=False
    )

    print("\nEnergy percentage table at last simulation instant:")
    print(percentage_table.to_string(index=False))
    plt.show()

    return fig, summary_df, percentage_table

if __name__ == "__main__":
    fig, summary_df, percentage_table = plot_global_energy_timeseries()
