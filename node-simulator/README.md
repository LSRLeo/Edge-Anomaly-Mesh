# Simulator

Quick rundown of what's here and how to run it.

## Layout

- **`simulation.py`** — Entry point (supports `sim` and `redis` commands).
- **`src/`** — Core logic (node, route, motion classes).
- **`routes/`** — Example route JSONs (e.g. `exampleHub.json`, `exampleHubLabel.json`).
- **`nodeConfig.json`** — Example node config (node_id, sample_rate_hz).
- **`redisFiles/`** — Redis support used by the `redis` command

Install deps first if you haven't: `pip install -r requirements.txt`.

---

## How to run

From the **`node-simulator`** directory.

### Simulation (`sim`)

Run the simulator from node and route config files. This generates the raw_data.json file that is required to then publish to Redis. You must choose **live** or **training** data mode which basically means whether you want your anomalies labled or not.

**Live data:**

```bash
python3 node-simulator/simulation.py sim -l -n nodeConfig.json -r routes/exampleHub.json
```

**Training data:**

```bash
python3 node-simulator/simulation.py sim -t -n nodeConfig.json -r routes/exampleHub.json
```

**`sim` arguments:**

| Argument | Short | Required | Description |
|----------|--------|----------|-------------|
| **Data mode** | | **Yes** (one of) | |
| `--live` | `-l` | | Use live data. |
| `--training` | `-t` | | Use training data. |
| `--node` | `-n` | Yes | Path to node config JSON (e.g. `nodeConfig.json`). |
| `--route` | `-r` | Yes | Path to route JSON (e.g. `routes/exampleHub.json`). |

You must pass exactly one of `-l` or `-t`; omitting both will error.

---

### Redis (`redis`)

Run with Redis (publish to a channel). This required the raw_data.json file to already be generated with `sim` as all it does is take those messages and publish them to a Redis channel. It batches messages and publishes 1 message/sec and publishes any messages that are generated within that 1 second.

```bash
python3 node-simulator/simulation.py redis [--host HOST] [--port PORT] CHANNEL_NAME
```

**Examples:**

```bash
python3 node-simulator/simulation.py redis sensor:raw
python3 node-simulator/simulation.py redis --host localhost --port 6379 sensor:raw
```

**`redis` arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--host` | `localhost` | Redis server hostname. |
| `--port` | `6379` | Redis server port. |
| `sensor:raw:*` | (required) | Name of the channel to monitor/publish to. |

---

### Help

```bash
python3 simulation.py -h
python3 simulation.py sim -h
python3 simulation.py redis -h
```

---

# Sprint 1 

## Summary

The basic motion simulator classes - Terrestrial, Maritime, Lift, and IDLE has been completed. Each class have methods that calculates distance between different hubs and generate acceleration&gyro (x,y,z) information. These information will be formatted and passed back to the node class. 

In addition, noise class has been implemented to add realisitc 'jitters' and small deviation in data from time to time based on the data that was provided by the client.


The route class will read from a json file containing information on the locations of each hub as well as transportation method between each hub. The route class will create hub objects accordingly.


the simulation class will use argparse to read and take in information from json files on Node an Route - a node and a route object will be created. 

the node class will take in sample rate and create the motion class objects. It will then use the location given by the route and pass them to the motion classes. Then they will be published.



## Example Input File (Route) -> You can find more example files in routes folder

{
    "hubs": [
      {
        "name": "Hub A",
        "gps_lat": 39.7392,
        "gps_lon": -104.9903,
        "alt": 1609.3,
        "time_at_hub": 1,
        "mode": "lift",
        "lift_time": 10
      },
      {
        "name": "Hub B",
        "gps_lat": 39.7392,
        "gps_lon": -104.9903,
        "alt": 1609.3,
        "time_at_hub": 1,
        "mode": "idle",
        "lift_time": 0
      }
    ]
  }

## Example Output

{
    "m_type": "raw-data",
    "m_id": "node_001_0",
    "event_id": "node_001_2026-02-21T19:03:54.468471",
    "node_id": "node_001",
    "timestamp": "2026-02-21T19:03:54.468471",
    "seq": 0,
    "gps": {
      "lat_deg": 39.7392,
      "lon_deg": -104.9903,
      "altitude_m": 1609.3
    },
    "accel_mss": {
      "x": 0.06250753081927615,
      "y": -0.04798519684978797,
      "z": 9.95887940949883
    },
    "gyro_rads": {
      "x": -0.010133946361581927,
      "y": 0.00397294283742329,
      "z": 0.0011543312753671878
    },
    "meta": {
      "sample_rate_hz": 1,
      "battery_pct": 95,
      "sim_mode": "IDLE",
      "sim_anomaly": false
    },
    "origin": {
      "lat_deg": 39.7392,
      "lon_deg": -104.9903,
      "altitude_m": 1609.3
    },
    "dest": {
      "lat_deg": 39.7392,
      "lon_deg": -104.9903,
      "altitude_m": 1609.3
    }
}

Key Constraint: Timestamps must increase monotonically; allow Team 2 to handle late arrivals

Shouldn't team1 create simulation data as well as pre-trained data?

Redis Channel
Channel: sensor:raw:{node_id}
Publisher: Node-simulator
Subscriber: ML & Databases



