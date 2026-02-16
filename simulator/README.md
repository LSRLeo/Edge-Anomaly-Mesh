# Simulator

Quick rundown of what’s here and how to run it.

## Layout

- **`simulation.py`** — Entry point
- **`src/`** — Core logic
- **`routes/`** — Example route JSONs: `exampleHub.json`
- **`nodeConfig.json`** — Example node config (node_id, sample_rate_hz).

## How to run

From the `simulator` directory:

```bash
python3 simulation.py -n nodeConfig.json -r routes/exampleHub.json
```

- **`-n` / `--node`** — Path to the node config JSON (e.g. `nodeConfig.json`).
- **`-r` / `--route`** — Path to the route JSON (e.g. `routes/exampleHub.json`).

Install deps first if you haven’t: `pip install -r requirements.txt`.
