from fps.parameters import RunConfig
from fps.simulate import FPSSimulation


def test_simulation_runs(tmp_path):
    cfg = RunConfig(T=0.1, Δt=0.05, n_strata=1)
    cfg.logging_every_step = 1
    cfg.log_format = "csv"
    cfg.run_name = "test"
    cfg.write_seed(tmp_path / "seeds.txt")
    sim = FPSSimulation(cfg)
    sim.run()
    log = tmp_path / "logs" / "test.csv"
    assert log.exists()
