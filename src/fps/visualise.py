import csv
from pathlib import Path
import matplotlib.pyplot as plt


def plot_log(path: str | Path) -> None:
    t, C = [], []
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            t.append(float(row["t"]))
            C.append(float(row["C"]))
    plt.plot(t, C)
    plt.xlabel("t")
    plt.ylabel("coherence")
    plt.show()
