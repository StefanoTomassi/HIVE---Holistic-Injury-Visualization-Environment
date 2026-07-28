from matplotlib.ticker import FormatStrFormatter, MaxNLocator
import pandas as pd
import matplotlib.pyplot as plt

from global_energy.get_part_energies import build_signal_metadata

SEPARATOR = ";"
HEADER_ROWS = 4  # detected in the file

def plot_seatbelt_measurements(csv_path: str):
    df = pd.read_csv(csv_path, sep=SEPARATOR, header=None)
    collect_and_plot_sliprings(df)
    collect_and_plot_retractors(df)
    collect_and_plot_belts(df)

def collect_and_plot_sliprings(df):
    time_mask = df.iloc[2].astype(str).str.contains("time", na=False)
    time = df.loc[:, time_mask][0]
    mask = df.iloc[2].astype(str).str.contains("ring_slip", na=False)
    slip_rings = df.loc[:, mask]
    slip_rings.insert(0, "time", time)
    for column in slip_rings.columns[1:]:
        newname = slip_rings[column].iloc[0]+"_"+slip_rings[column].iloc[1]
        slip_rings = slip_rings.rename(columns={column: newname})
    slip_rings = slip_rings.drop([0, 1, 2, 3])
    slip_rings = slip_rings.reset_index(drop=True)
    slip_rings = slip_rings.apply(pd.to_numeric, errors='coerce')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax = plt.gca()

    for column in slip_rings.columns[1:]:
        ax.plot(slip_rings["time"], slip_rings[column], label=column)

    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("ring_slip [-]")
    ax.set_title("Slip Ring Measurements")
    ax.legend()
    plt.show()

def collect_and_plot_retractors(df):
    time_mask = df.iloc[2].astype(str).str.contains("time", na=False)
    time = df.loc[:, time_mask][0]
    mask = (
        df.iloc[2].astype(str).str.contains("retractor_pull_out", na=False)
    | df.iloc[2].astype(str).str.contains("retractor_force", na=False)
    )
    retractors = df.loc[:, mask]
    retractors.insert(0, "time", time)

    for column in retractors.columns[1:]:
        newname = retractors[column].iloc[0]+"_"+retractors[column].iloc[1]
        retractors = retractors.rename(columns={column: newname})
    retractors = retractors.drop([0, 1, 2, 3])
    retractors = retractors.reset_index(drop=True)
    retractors = retractors.apply(pd.to_numeric, errors='coerce')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax = plt.gca()

    for_measure = retractors.columns[retractors.columns.str.contains("force", case=False)]
    pullout_measure = retractors.columns[retractors.columns.str.contains("pull_out", case=False)]

    for column in pullout_measure:
        ax.plot(retractors["time"], retractors[column], label=column)

    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("retractor_pull_out [-]")
    ax.set_title("Retractor Measurements")
    ax.legend()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax = plt.gca()
    
    for column in for_measure:
            ax.plot(retractors["time"], retractors[column], label=column)
    
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("retractor_force [-]")
    ax.set_title("Retractor Measurements")
    ax.legend()
    plt.show()

def collect_and_plot_belts(df):
    time_mask = df.iloc[2].astype(str).str.contains("time", na=False)
    time = df.loc[:, time_mask][0]
    mask = (
        df.iloc[2].astype(str).str.contains("belt_length", na=False)
    | df.iloc[2].astype(str).str.contains("belt_force", na=False)
    )
    belts = df.loc[:, mask]
    belts.insert(0, "time", time)

    for column in belts.columns[1:]:
        newname = belts[column].iloc[0]+"_"+belts[column].iloc[1]
        belts = belts.rename(columns={column: newname})
    belts = belts.drop([0, 1, 2, 3])
    belts = belts.reset_index(drop=True)
    belts = belts.apply(pd.to_numeric, errors='coerce')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax = plt.gca()

    for_measure = belts.columns[belts.columns.str.contains("force", case=False)]
    length_measure = belts.columns[belts.columns.str.contains("length", case=False)]

    for column in length_measure:
        ax.plot(belts["time"], belts[column], label=column)

    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("belt_length [-]")
    ax.set_title("Belt Measurements")
    ax.legend()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax = plt.gca()
    
    for column in for_measure:
            ax.plot(belts["time"], belts[column], label=column)
    
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax.set_xlabel("Time [ms]")
    ax.set_ylabel("belt_force [-]")
    ax.set_title("Belt Measurements")
    ax.legend()
    plt.show()