import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#Plot settings
# -----------------------------
# Figure size (Tufte layout) - MODIFICATO
# -----------------------------
width_cm = 17.75 / 3 * 1.5  # Aumentato del 50% per nitidezza in Word
golden_ratio = (1 + 5**0.5) / 2
height_cm = width_cm / golden_ratio
cm_to_inch = 1 / 2.54
figsize = (width_cm * cm_to_inch, height_cm * cm_to_inch)

# DPI fisso alto per esportazione SVG/PDF
plt.rcParams['figure.dpi'] = 300  # AGGIUNTO

# -----------------------------
# Matplotlib style - MODIFICATO
# -----------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": "Calibri",  # Sostituiti Calibri
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.5,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.dpi": 300,  # AGGIUNTO per esportazioni
    "figure.autolayout": True,  # AGGIUNTO per evitare sovrapposizioni
})
# -----------------------------

# Nice color scheme (Okabe-Ito)

# -----------------------------

c33 = "#0072B2"   # blue

c40 = "#D55E00"   # vermillion

# -----------------------------

# Pulses to compare

# -----------------------------

pulses = [33, 40]

colors = {33: c33, 40: c40}