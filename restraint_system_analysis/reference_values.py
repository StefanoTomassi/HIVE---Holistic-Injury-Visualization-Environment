"""Reference limits and risk functions for HBM frontal-impact injury criteria.

Order of precedence (see the restraint-analysis plan):

1. Supervisor values: ``whiplash_analysis.reference_values`` holds neck
   tissue limits only (ligament strain, ROM, facet/disc loads, muscle stress).
   None of them overlaps the criteria computed here, so they are not reused.
2. VIVA+ developers' risk functions, copied from the Dynasaur files shipped
   with the model (``model/postprocess/Dynasaur``). These are model-specific
   and are the primary measure for the HBM.
3. Regulatory / consumer-test limits (Hybrid III 50M). These are
   **ATD limits and are shown for the HBM as indicative values only.**

Units follow the HIVE Dynasaur unit block (ms, mm, kg) unless stated.
Values were cross-checked on 2026-11-13; see the ``SOURCES`` mapping.
The textbook reference for the criteria definitions is Schmitt, Niederer,
Cronin, Morrison, Muser, Walz: *Trauma Biomechanics*, Springer (chapters on
head, neck, thorax and lower-extremity injuries).
"""

import math
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np


@dataclass(frozen=True)
class Limit:
    """One injury criterion limit.

    Attributes:
        value: Threshold value in ``unit``.
        unit: Unit of the value.
        source: Short citation key in :data:`SOURCES`.
        band: ``"regulatory"``, ``"higher_performance"``, ``"lower_performance"``
            or ``"tolerance"``.
        note: Free text (risk level, dummy, etc.).
    """

    value: float
    unit: str
    source: str
    band: str
    note: str = ""


SOURCES: Dict[str, str] = {
    "FMVSS208": (
        "49 CFR 571.208 (FMVSS 208) Hybrid III 50th male limits, as tabulated in "
        "NHTSA compliance test reports, e.g. "
        "https://nrd-static.nhtsa.dot.gov/reports/vehdb/v00000/v02800/v02832R001.pdf"
    ),
    "EuroNCAP": (
        "Euro NCAP-derived adult occupant assessment (frontal, Hybrid III 50M), "
        "Global NCAP Assessment Protocol Adult 2021, sec. 3.1"
    ),
    "Takhounts2013": (
        "Takhounts EG et al. Development of Brain Injury Criteria (BrIC). "
        "Stapp Car Crash J 57:243-266, 2013"
    ),
    "Bostrom1996": (
        "Bostrom O et al. A new neck injury criterion candidate based on injury "
        "findings in the cervical spinal ganglia after experimental neck "
        "extension trauma. IRCOBI 1996"
    ),
    "Larsson2021": (
        "Larsson KJ et al. Rib cortical bone fracture risk as a function of age "
        "and rib strain. Front Bioeng Biotechnol 9:677768, 2021 "
        "(as implemented in VIVA+ ls_user_function.py)"
    ),
    "VIVAplus": "VIVA+ 2.0.1 Dynasaur post-processing files (model/postprocess/Dynasaur)",
    "NHTSA_HIC": (
        "NHTSA head injury risk curve for HIC15 (NCAP upgrade, 73 FR 40016, "
        "11 July 2008, docket NHTSA-2006-26555): P(AIS n+) = Phi((ln HIC15 - mu) / "
        "sigma); AIS2+ and AIS3+ parameters as tabulated in 27th ESV paper "
        "27ESV-000149, Table 1"
    ),
    "AIS2005": (
        "AAAM Abbreviated Injury Scale 2005 (update 2008): rib fractures - 1 rib AIS 1, "
        "2 ribs AIS 2, 3 or more ribs AIS 3"
    ),
}

#: Abbreviated Injury Scale in plain words (AAAM AIS 2005).
AIS_DESCRIPTIONS = {
    1: ("Minor", "e.g. bruise, whiplash, single rib fracture"),
    2: ("Moderate", "e.g. concussion, two rib fractures, simple bone fracture"),
    3: ("Serious", "e.g. three or more rib fractures, skull fracture"),
    4: ("Severe", "e.g. brain bleeding, flail chest - life-threatening"),
    5: ("Critical", "survival uncertain"),
    6: ("Maximal", "currently untreatable"),
}

#: Log-normal HIC risk curves (NHTSA_HIC): AIS level -> (mu, sigma).
HIC_RISK_LOGNORMAL = {
    "AIS2+": (6.96352, 0.84664),
    "AIS3+": (7.45231, 0.73998),
}


def hic_risk(hic: float, level: str) -> float:
    """Probability of head injury of AIS ``level`` (``"AIS2+"``/``"AIS3+"``) for HIC."""
    if hic is None or not hic > 0:
        return 0.0
    mu, sigma = HIC_RISK_LOGNORMAL[level]
    return 0.5 * (1.0 + math.erf((math.log(hic) - mu) / (sigma * math.sqrt(2.0))))


def fractured_rib_distribution(risks) -> list:
    """P(exactly k ribs fractured), k = 0..n, for independent per-rib risks.

    Poisson-binomial distribution, as used with the Larsson 2021 risk function
    to estimate the number of fractured ribs (NFR).
    """
    distribution = [1.0]
    for p in risks:
        updated = [0.0] * (len(distribution) + 1)
        for k, value in enumerate(distribution):
            updated[k] += value * (1.0 - p)
            updated[k + 1] += value * p
        distribution = updated
    return distribution

# --- Head --------------------------------------------------------------------
HIC15_LIMITS = {
    "FMVSS 208": Limit(700.0, "-", "FMVSS208", "regulatory"),
    "Euro NCAP higher": Limit(500.0, "-", "EuroNCAP", "higher_performance"),
    "Euro NCAP lower": Limit(700.0, "-", "EuroNCAP", "lower_performance",
                             "approx. 20 % risk of AIS3+"),
}

#: BrIC critical angular velocities [rad/s], Hybrid III 50M (Takhounts 2013).
BRIC_CRITICAL_OMEGA = {"x": 66.25, "y": 56.45, "z": 42.87}
BRIC_LIMITS = {
    "BrIC = 1": Limit(1.0, "-", "Takhounts2013", "tolerance",
                      "critical value of the normalised angular velocity"),
}

#: VIVA+ head DAMAGE parameters (10_head.def).
HEAD_DAMAGE_PARAMETERS = {
    "mx": 1, "my": 1, "mz": 1,
    "kxx": 32142, "kyy": 23493, "kzz": 16935,
    "kxy": 0, "kyz": 0, "kxz": 1636.3,
    "a0": 0, "a1": 0.0059148, "beta": 2.9903,
}
#: Extended Weibull risk parameters of DAMAGE (10_head.def): AIS level -> params.
HEAD_DAMAGE_RISK = {
    "AIS1": {"a": -0.93140437, "b": 0.245218244, "c": 0.017, "d": 0.957},
    "AIS2": {"a": -0.778705069, "b": 0.258064516, "c": 0.017, "d": 0.957},
    "AIS4+": {"a": -0.436955775, "b": 0.16526194, "c": 0.017, "d": 0.957},
}

# --- Neck --------------------------------------------------------------------
NIC_LIMITS = {
    "NIC tolerance": Limit(15.0, "m^2/s^2", "Bostrom1996", "tolerance",
                           "proposed for AIS1 (rear impact); indicative in frontal"),
}
#: VIVA+ NIC risk sigmoid (20_neck_injury_criteria.def).
NIC_RISK_SIGMOID = {"k": 0.21, "x0": 15.952380952380953}

NECK_LIMITS = {
    "Nij FMVSS 208": Limit(1.0, "-", "FMVSS208", "regulatory"),
    "Tension FMVSS 208": Limit(4170.0, "N", "FMVSS208", "regulatory"),
    "Compression FMVSS 208": Limit(4000.0, "N", "FMVSS208", "regulatory"),
    "Tension Euro NCAP higher": Limit(2700.0, "N", "EuroNCAP", "higher_performance",
                                      "at 0 ms (cumulative exceedance)"),
    "Tension Euro NCAP lower": Limit(3300.0, "N", "EuroNCAP", "lower_performance",
                                     "at 0 ms (cumulative exceedance)"),
    "Extension Euro NCAP higher": Limit(42.0, "Nm", "EuroNCAP", "higher_performance"),
    "Extension Euro NCAP lower": Limit(57.0, "Nm", "EuroNCAP", "lower_performance"),
}

# --- Thorax ------------------------------------------------------------------
CHEST_DEFLECTION_LIMITS = {
    "FMVSS 208": Limit(63.0, "mm", "FMVSS208", "regulatory"),
    "Euro NCAP higher": Limit(22.0, "mm", "EuroNCAP", "higher_performance",
                              "5 % risk of AIS3+"),
    "Euro NCAP lower": Limit(42.0, "mm", "EuroNCAP", "lower_performance"),
}
#: Larsson 2021 age-dependent rib fracture risk (VIVA+ ls_user_function.py).
RIB_RISK_ERF = {"a": 0.3026, "b": -2.9866, "c": -0.013}
RIB_RISK_AGES = (25, 50, 75)

# --- Lower body --------------------------------------------------------------
FEMUR_LIMITS = {
    "FMVSS 208": Limit(10.0, "kN", "FMVSS208", "regulatory"),
    "Euro NCAP higher": Limit(3.8, "kN", "EuroNCAP", "higher_performance",
                              "5 % risk of pelvis injury"),
    "Euro NCAP lower": Limit(9.07, "kN", "EuroNCAP", "lower_performance",
                             "at 0 ms (femur fracture limit)"),
}


def bric(omega_x: np.ndarray, omega_y: np.ndarray, omega_z: np.ndarray) -> float:
    """Brain Injury Criterion from head angular velocities in rad/s."""
    peaks = [float(np.nanmax(np.abs(component)))
             for component in (omega_x, omega_y, omega_z)]
    return math.sqrt(sum(
        (peak / BRIC_CRITICAL_OMEGA[axis]) ** 2
        for peak, axis in zip(peaks, ("x", "y", "z"))
    ))


def rib_fracture_risk(strain: float, age: float) -> float:
    """Larsson 2021 rib fracture probability for a peak tensile strain [-]."""
    if not strain or strain <= 0 or math.isnan(strain):
        return 0.0
    a, b, c = RIB_RISK_ERF["a"], RIB_RISK_ERF["b"], RIB_RISK_ERF["c"]
    return 0.5 + 0.5 * math.erf((math.log(strain) - (b + c * age)) / (math.sqrt(2) * a))


def limits_for(criterion: str) -> Optional[Dict[str, Limit]]:
    """Return the limit dictionary for a HIVE criterion key, if any."""
    return {
        "HIC15": HIC15_LIMITS,
        "BrIC": BRIC_LIMITS,
        "NIC_max": NIC_LIMITS,
        "chest_deflection_max": CHEST_DEFLECTION_LIMITS,
        "femur_force_max": FEMUR_LIMITS,
    }.get(criterion)
