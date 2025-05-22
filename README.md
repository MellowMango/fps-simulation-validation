# FPS Simulation & Validation Toolkit (v0.1)

A minimal-yet-rigorous code scaffold for reproducing, stress-testing, and visualising the Fractale Pulsante Spiralée (FPS) model. Designed for fast iteration, statistical reproducibility, and transparent peer review.

## Quick start

1. **Install dependencies**

   ```bash
   pip install -e .
   ```

2. **Run a baseline simulation**

   ```bash
   python -m fps.simulate --config config/default.yaml
   ```

   Results are written to `data/logs/`. Adjust parameters in
   `config/default.yaml` to experiment with different settings.

3. **Launch the web server** (requires `uvicorn`)

   ```bash
   uvicorn fps.server:app --reload
   ```

   Trigger a run via

   ```bash
   curl -X POST http://127.0.0.1:8000/run
   ```

   View the coherence plot at

   ```bash
   http://127.0.0.1:8000/plot/<run_name>
   ```

   Replace `<run_name>` with the `run_name` specified in the config.
