from __future__ import annotations
from pydantic import BaseModel, Field, validator
from pathlib import Path
from typing import Literal

class FeedbackConfig(BaseModel):
    G: Literal["tanh", "damped_sine", "sinc", "custom"] = "tanh"

class NoiseConfig(BaseModel):
    type: Literal["uniform", "gaussian", "real_signal"] = "uniform"
    scale: float = Field(0.0, ge=0)

class StrataDefaults(BaseModel):
    A0: float = 1.0
    f0: float = 1.0
    φ0: float = 0.0
    γ0: float = 1.0
    α: float = 0.1
    β: float = 0.05
    λ: float = 0.01

class RunConfig(BaseModel):
    run_name: str = "baseline"
    seed: int | None = None
    T: float = Field(..., gt=0)
    Δt: float = Field(..., gt=0)
    n_strata: int = Field(..., ge=1)
    strata_defaults: StrataDefaults = StrataDefaults()
    feedback: FeedbackConfig = FeedbackConfig()
    noise: NoiseConfig = NoiseConfig()
    logging_every_step: int = 10
    log_format: Literal["csv", "hdf5"] = "csv"

    @validator("logging_every_step")
    def nonzero(cls, v):
        if v < 1:
            raise ValueError("logging_every_step must be ≥1")
        return v

    def write_seed(self, path: Path = Path("data/seeds.txt")) -> None:
        if self.seed is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            f.write(f"{self.run_name},{self.seed}\n")
