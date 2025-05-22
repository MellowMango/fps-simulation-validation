from fastapi import FastAPI, Response
from pathlib import Path
from io import BytesIO
import csv
import yaml
import matplotlib.pyplot as plt

from .simulate import FPSSimulation
from .parameters import RunConfig

app = FastAPI()


def _load_cfg(cfg_path: str) -> RunConfig:
    with open(cfg_path, "r") as f:
        cfg_dict = yaml.safe_load(f)
    logging_cfg = cfg_dict.get("logging", {})
    return RunConfig(
        run_name=cfg_dict.get("run_name", "run"),
        seed=cfg_dict.get("seed"),
        T=cfg_dict.get("T", 1.0),
        Δt=cfg_dict.get("Δt", 0.01),
        n_strata=cfg_dict.get("n_strata", 1),
        strata_defaults=cfg_dict.get("strata_defaults", {}),
        feedback=cfg_dict.get("feedback", {}),
        noise=cfg_dict.get("noise", {}),
        logging_every_step=logging_cfg.get("every_step", 10),
        log_format=logging_cfg.get("format", "csv"),
    )


@app.post("/run")
def run_simulation(cfg_path: str = "config/default.yaml"):
    cfg = _load_cfg(cfg_path)
    sim = FPSSimulation(cfg)
    sim.run()
    return {"status": "ok", "run_name": cfg.run_name}


@app.get("/plot/{run_name}")
def plot(run_name: str):
    log_path = Path("data/logs") / f"{run_name}.csv"
    if not log_path.exists():
        return {"error": "log not found"}
    t, C = [], []
    with log_path.open() as f:
        r = csv.DictReader(f)
        for row in r:
            t.append(float(row["t"]))
            C.append(float(row["C"]))
    fig, ax = plt.subplots()
    ax.plot(t, C)
    ax.set_xlabel("t")
    ax.set_ylabel("coherence")
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return Response(buf.getvalue(), media_type="image/png")
