import numpy as np
from dataclasses import dataclass

@dataclass
class Stratum:
    A: float
    f: float
    φ: float
    γ: float
    α: float
    β: float
    λ: float

    def update(self, I: float, feedback: float, Δt: float) -> None:
        """Update state according to Eq. (1) discretisation."""
        I_filt = 1 / (1 + np.exp(-I))
        self.A += self.α * I_filt - self.β * feedback
        self.f += self.λ * feedback
        self.φ = (self.φ + 2 * np.pi * self.f * Δt) % (2 * np.pi)
