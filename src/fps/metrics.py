import numpy as np
from .strata import Stratum


def coherence(strata: list[Stratum]) -> float:
    phases = np.array([s.φ for s in strata])
    mean_phase = np.angle(np.mean(np.exp(1j * phases)))
    return float(np.mean(np.cos(phases - mean_phase)))


def effort(strata: list[Stratum]) -> float:
    # simple placeholder effort as sum of amplitudes
    return float(sum(abs(s.A) for s in strata))
