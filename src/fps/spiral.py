import numpy as np
from typing import Callable


def G_factory(kind: str) -> Callable[[float], float]:
    if kind == "tanh":
        return lambda x: np.tanh(x)
    if kind == "damped_sine":
        return lambda x: np.exp(-np.abs(x)) * np.sin(x)
    if kind == "sinc":
        return lambda x: np.sinc(x / np.pi)
    raise ValueError(f"Unknown G kind: {kind}")
