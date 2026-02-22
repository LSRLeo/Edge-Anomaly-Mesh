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



# Sprint 1 

## Summary

The basic motion simulator classes - Terrestrial, Maritime, Lift, and IDLE has been completed. Each class have methods that calculates distance between different hubs and generate acceleration&gyro (x,y,z) information. These information will be formatted and passed back to the node class. 

In addition, noise class has been implemented to add realisitc 'jitters' and small deviation in data from time to time based on the data that was provided by the client.


The route class will read from a json file containing information on the locations of each hub as well as transportation method between each hub. The route class will create hub objects accordingly.


the simulation class will use argparse to read and take in information from json files on Node an Route - a node and a route object will be created. 

the node class will take in sample rate and create the motion class objects. It will then use the location given by the route and pass them to the motion classes. Then they will be published.


## Example Output