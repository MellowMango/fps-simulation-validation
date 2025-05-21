import numpy as np
import time
import csv
from pathlib import Path
from .parameters import RunConfig
from .strata import Stratum
from .spiral import G_factory
from .metrics import coherence, effort


class FPSSimulation:
    def __init__(self, cfg: RunConfig):
        self.cfg = cfg
        self.G = G_factory(cfg.feedback.G)
        rng = np.random.default_rng(cfg.seed)
        self.noise = rng
        self.strata = [
            Stratum(
                cfg.strata_defaults.A0,
                cfg.strata_defaults.f0,
                cfg.strata_defaults.φ0,
                cfg.strata_defaults.γ0,
                cfg.strata_defaults.α,
                cfg.strata_defaults.β,
                cfg.strata_defaults.λ,
            )
            for _ in range(cfg.n_strata)
        ]
        self.steps = int(cfg.T / cfg.Δt)
        self._prepare_logging()
        cfg.write_seed()

    def _prepare_logging(self) -> None:
        self.rows: list[tuple[float, float, float, float]] = []
        self.t0 = time.perf_counter()

    def run(self) -> None:
        for k in range(self.steps):
            t = k * self.cfg.Δt
            for s in self.strata:
                I = self.noise.uniform(-1, 1) * self.cfg.noise.scale
                feedback = self.G(I)
                s.update(I, feedback, self.cfg.Δt)
            if k % self.cfg.logging_every_step == 0:
                self._log_step(t)
        self._dump()

    def _log_step(self, t: float) -> None:
        C = coherence(self.strata)
        E = effort(self.strata)
        cpu = (time.perf_counter() - self.t0) / (len(self.rows) + 1)
        self.rows.append((t, C, E, cpu))

    def _dump(self) -> None:
        out = Path("data/logs")
        out.mkdir(parents=True, exist_ok=True)
        fname = out / f"{self.cfg.run_name}.{self.cfg.log_format}"
        if self.cfg.log_format == "csv":
            with fname.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["t", "C", "effort", "cpu_step"])
                w.writerows(self.rows)
        else:
            import h5py

            with h5py.File(fname, "w") as h5:
                h5.create_dataset("dataset", data=np.array(self.rows))


def main(argv=None) -> None:
    import argparse, yaml

    parser = argparse.ArgumentParser(description="Run FPS simulation")
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args(argv)

    with open(args.config, "r") as f:
        cfg_dict = yaml.safe_load(f)
    logging_cfg = cfg_dict.get("logging", {})
    cfg = RunConfig(
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
    sim = FPSSimulation(cfg)
    sim.run()


if __name__ == "__main__":
    main()
