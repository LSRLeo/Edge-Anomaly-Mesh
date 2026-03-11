import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Visualize latitude/longitude from a simulator raw data JSON file.\n\n"
            "The filename is interpreted relative to the node-simulator directory.\n"
            "If omitted, defaults to 'raw_data.json'."
        )
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default="raw_data.json",
        help="Name or path of the simulation JSON file (relative to node-simulator).",
    )
    parser.add_argument(
        "--hubs",
        metavar="ROUTE_JSON",
        default=None,
        help="Path to a route JSON file (e.g. routes/exampleHub.json). Hubs are plotted in black with labels.",
    )
    return parser.parse_args()


def load_lat_lon(json_path: Path):
    if not json_path.exists():
        raise FileNotFoundError(f"Simulation file not found: {json_path}")

    with json_path.open("r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a list of messages in {json_path}, got {type(data)}")

    lats = []
    lons = []
    alts = []
    motion_types = []
    anomaly_flags = []
    for msg in data:
        gps = msg.get("gps") or {}
        lat = gps.get("lat_deg")
        lon = gps.get("lon_deg")
        alt = gps.get("altitude_m")
        if lat is not None and lon is not None and alt is not None:
            lats.append(lat)
            lons.append(lon)
            alts.append(alt)
            meta = msg.get("meta") or {}
            motion_types.append(meta.get("motion_type"))
            # Treat anything truthy and not an explicit "False" string as anomalous
            raw_flag = meta.get("is_anomaly")
            is_anom = False
            if isinstance(raw_flag, bool):
                is_anom = raw_flag
            elif isinstance(raw_flag, str):
                is_anom = raw_flag.lower() not in ("", "false", "0", "none")
            elif raw_flag is not None:
                is_anom = True
            anomaly_flags.append(is_anom)

    return lats, lons, alts, motion_types, anomaly_flags


def load_hubs_from_route(route_path: Path):
    """Load hub lat, lon, altitude_m and label from a route JSON. Returns list of dicts."""
    if not route_path.exists():
        raise FileNotFoundError(f"Route file not found: {route_path}")
    with route_path.open("r") as f:
        data = json.load(f)
    hubs = data.get("hubs") or []
    out = []
    for h in hubs:
        lat = h.get("lat")
        lon = h.get("lon")
        alt = h.get("altitude_m")
        if lat is None or lon is None:
            continue
        if alt is None:
            alt = 0.0
        label = h.get("name") or h.get("hub_id") or "Hub"
        out.append({"lat": lat, "lon": lon, "alt": alt, "label": str(label)})
    return out


def _compute_square_limits(xs, ys):
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    if min_x == max_x:
        span_x = 1e-4
    else:
        span_x = max_x - min_x

    if min_y == max_y:
        span_y = 1e-4
    else:
        span_y = max_y - min_y

    full_span = max(span_x, span_y)
    half_span = full_span / 2.0

    center_x = (max_x + min_x) / 2.0
    center_y = (max_y + min_y) / 2.0

    return (center_x - half_span, center_x + half_span), (center_y - half_span, center_y + half_span)


def _plot_hubs(ax, hubs, kind, color="black"):
    """Plot hubs on an axis. kind is 'lat_lon', 'lat_alt', 'lon_alt', or '3d'."""
    if not hubs:
        return
    if kind == "lat_lon":
        xs = [h["lon"] for h in hubs]
        ys = [h["lat"] for h in hubs]
        ax.scatter(xs, ys, s=80, c=color, marker="s", zorder=5, edgecolors="black", linewidths=1.5, label="Hubs")
        for h in hubs:
            ax.annotate(h["label"], (h["lon"], h["lat"]), xytext=(4, 4), textcoords="offset points", fontsize=7, color=color)
    elif kind == "lat_alt":
        xs = [h["lat"] for h in hubs]
        ys = [h["alt"] for h in hubs]
        ax.scatter(xs, ys, s=80, c=color, marker="s", zorder=5, edgecolors="black", linewidths=1.5, label="Hubs")
        for h in hubs:
            ax.annotate(h["label"], (h["lat"], h["alt"]), xytext=(4, 4), textcoords="offset points", fontsize=7, color=color)
    elif kind == "lon_alt":
        xs = [h["lon"] for h in hubs]
        ys = [h["alt"] for h in hubs]
        ax.scatter(xs, ys, s=80, c=color, marker="s", zorder=5, edgecolors="black", linewidths=1.5, label="Hubs")
        for h in hubs:
            ax.annotate(h["label"], (h["lon"], h["alt"]), xytext=(4, 4), textcoords="offset points", fontsize=7, color=color)
    elif kind == "3d":
        xs = [h["lon"] for h in hubs]
        ys = [h["lat"] for h in hubs]
        zs = [h["alt"] for h in hubs]
        ax.scatter(xs, ys, zs, s=80, c=color, marker="s", depthshade=False, label="Hubs")
        for h in hubs:
            ax.text(h["lon"], h["lat"], h["alt"], h["label"], fontsize=7, color=color)


def plot_views(lats, lons, alts, motion_types, anomaly_flags, title: str, hubs=None):
    if not lats or not lons or not alts:
        print("No GPS latitude/longitude/altitude data found to plot.")
        return

    has_motion_types = any(mt is not None for mt in motion_types)
    color_map = {
        "IDLE": "orange",
        "TERRESTRIAL": "green",
        "MARITIME": "blue",
        "LIFT": "purple",
    }
    anomaly_color_map = {
        "IDLE": "#ff69b4",         # pink
        "TERRESTRIAL": "#800080",  # purple
        "MARITIME": "#ff0000",     # red
        "LIFT": "#8a2be2",         # violet
    }

    # Full-page style figure
    fig = plt.figure(figsize=(12, 10))

    # 1) Lat vs Lon (top-left)
    ax1 = fig.add_subplot(2, 2, 1)

    if not has_motion_types:
        ax1.plot(lons, lats, "-", linewidth=1.0, alpha=0.8, color="black")
        ax1.scatter(lons, lats, s=5, alpha=0.6, color="black")
    else:
        start_idx = 0
        current_type = motion_types[0]
        current_anom = anomaly_flags[0]
        for i in range(1, len(lats)):
            if motion_types[i] != current_type or anomaly_flags[i] != current_anom:
                segment_lons = lons[start_idx:i]
                segment_lats = lats[start_idx:i]
                if current_anom:
                    color = anomaly_color_map.get(current_type, "red")
                else:
                    color = color_map.get(current_type, "red")
                if len(segment_lats) > 1:
                    ax1.plot(segment_lons, segment_lats, "-", linewidth=1.0, alpha=0.8, color=color)
                start_idx = i
                current_type = motion_types[i]
                current_anom = anomaly_flags[i]

        segment_lons = lons[start_idx:]
        segment_lats = lats[start_idx:]
        if current_anom:
            color = anomaly_color_map.get(current_type, "red")
        else:
            color = color_map.get(current_type, "red")
        if len(segment_lats) > 1:
            ax1.plot(segment_lons, segment_lats, "-", linewidth=1.0, alpha=0.8, color=color)

        # Scatter all points, colored by motion type and anomaly status
        for mt in color_map.keys():
            # Non-anomalous points for this motion type
            xs = [lon for lon, m, a in zip(lons, motion_types, anomaly_flags) if m == mt and not a]
            ys = [lat for lat, m, a in zip(lats, motion_types, anomaly_flags) if m == mt and not a]
            if xs:
                ax1.scatter(xs, ys, s=5, alpha=0.6, color=color_map[mt], label=f"{mt}")
            # Anomalous points for this motion type
            xs_a = [lon for lon, m, a in zip(lons, motion_types, anomaly_flags) if m == mt and a]
            ys_a = [lat for lat, m, a in zip(lats, motion_types, anomaly_flags) if m == mt and a]
            if xs_a:
                ax1.scatter(xs_a, ys_a, s=8, alpha=0.8, color=anomaly_color_map[mt], label=f"{mt} (anom)")

        xs_unknown = [lon for lon, m in zip(lons, motion_types) if m not in color_map and m is not None]
        ys_unknown = [lat for lat, m in zip(lats, motion_types) if m not in color_map and m is not None]
        if xs_unknown:
            ax1.scatter(xs_unknown, ys_unknown, s=5, alpha=0.6, color="red", label="OTHER")

        ax1.legend(loc="best", fontsize="x-small")

    ax1.set_xlabel("Longitude (deg)")
    ax1.set_ylabel("Latitude (deg)")
    ax1.set_title("Lat vs Lon")
    xlim, ylim = _compute_square_limits(lons, lats)
    ax1.set_xlim(*xlim)
    ax1.set_ylim(*ylim)
    ax1.set_aspect("equal", adjustable="box")
    _plot_hubs(ax1, hubs or [], "lat_lon", color="black")

    # 2) Lat vs Alt (top-right)
    ax2 = fig.add_subplot(2, 2, 2)
    if not has_motion_types:
        ax2.plot(lats, alts, "-", linewidth=1.0, alpha=0.8, color="black")
        ax2.scatter(lats, alts, s=5, alpha=0.6, color="black")
    else:
        # Draw line segments per contiguous (motion_type, anomaly) run
        start_idx = 0
        current_type = motion_types[0]
        current_anom = anomaly_flags[0]
        for i in range(1, len(lats)):
            if motion_types[i] != current_type or anomaly_flags[i] != current_anom:
                segment_lats = lats[start_idx:i]
                segment_alts = alts[start_idx:i]
                if current_anom:
                    color = anomaly_color_map.get(current_type, "red")
                else:
                    color = color_map.get(current_type, "red")
                if len(segment_lats) > 1:
                    ax2.plot(segment_lats, segment_alts, "-", linewidth=1.0, alpha=0.8, color=color)
                start_idx = i
                current_type = motion_types[i]
                current_anom = anomaly_flags[i]

        segment_lats = lats[start_idx:]
        segment_alts = alts[start_idx:]
        if current_anom:
            color = anomaly_color_map.get(current_type, "red")
        else:
            color = color_map.get(current_type, "red")
        if len(segment_lats) > 1:
            ax2.plot(segment_lats, segment_alts, "-", linewidth=1.0, alpha=0.8, color=color)

        for mt in color_map.keys():
            xs = [lat for lat, m, a in zip(lats, motion_types, anomaly_flags) if m == mt and not a]
            ys = [alt for alt, m, a in zip(alts, motion_types, anomaly_flags) if m == mt and not a]
            if xs:
                ax2.scatter(xs, ys, s=5, alpha=0.6, color=color_map[mt])
            xs_a = [lat for lat, m, a in zip(lats, motion_types, anomaly_flags) if m == mt and a]
            ys_a = [alt for alt, m, a in zip(alts, motion_types, anomaly_flags) if m == mt and a]
            if xs_a:
                ax2.scatter(xs_a, ys_a, s=5, alpha=0.8, color=anomaly_color_map[mt])
    ax2.set_xlabel("Latitude (deg)")
    ax2.set_ylabel("Altitude (m)")
    ax2.set_title("Lat vs Alt")
    _plot_hubs(ax2, hubs or [], "lat_alt", color="black")

    # 3) Lon vs Alt (bottom-left)
    ax3 = fig.add_subplot(2, 2, 3)
    if not has_motion_types:
        ax3.plot(lons, alts, "-", linewidth=1.0, alpha=0.8, color="black")
        ax3.scatter(lons, alts, s=5, alpha=0.6, color="black")
    else:
        start_idx = 0
        current_type = motion_types[0]
        current_anom = anomaly_flags[0]
        for i in range(1, len(lons)):
            if motion_types[i] != current_type or anomaly_flags[i] != current_anom:
                segment_lons = lons[start_idx:i]
                segment_alts = alts[start_idx:i]
                if current_anom:
                    color = anomaly_color_map.get(current_type, "red")
                else:
                    color = color_map.get(current_type, "red")
                if len(segment_lons) > 1:
                    ax3.plot(segment_lons, segment_alts, "-", linewidth=1.0, alpha=0.8, color=color)
                start_idx = i
                current_type = motion_types[i]
                current_anom = anomaly_flags[i]

        segment_lons = lons[start_idx:]
        segment_alts = alts[start_idx:]
        if current_anom:
            color = anomaly_color_map.get(current_type, "red")
        else:
            color = color_map.get(current_type, "red")
        if len(segment_lons) > 1:
            ax3.plot(segment_lons, segment_alts, "-", linewidth=1.0, alpha=0.8, color=color)

        for mt in color_map.keys():
            xs = [lon for lon, m, a in zip(lons, motion_types, anomaly_flags) if m == mt and not a]
            ys = [alt for alt, m, a in zip(alts, motion_types, anomaly_flags) if m == mt and not a]
            if xs:
                ax3.scatter(xs, ys, s=5, alpha=0.6, color=color_map[mt])
            xs_a = [lon for lon, m, a in zip(lons, motion_types, anomaly_flags) if m == mt and a]
            ys_a = [alt for alt, m, a in zip(alts, motion_types, anomaly_flags) if m == mt and a]
            if xs_a:
                ax3.scatter(xs_a, ys_a, s=5, alpha=0.8, color=anomaly_color_map[mt])
    ax3.set_xlabel("Longitude (deg)")
    ax3.set_ylabel("Altitude (m)")
    ax3.set_title("Lon vs Alt")
    _plot_hubs(ax3, hubs or [], "lon_alt", color="black")

    # 4) 3D Lon, Lat, Alt (bottom-right)
    ax4 = fig.add_subplot(2, 2, 4, projection="3d")
    if not has_motion_types:
        ax4.plot(lons, lats, alts, linewidth=0.8, alpha=0.9, color="black")
        ax4.scatter(lons, lats, alts, s=4, alpha=0.6, color="black")
    else:
        start_idx = 0
        current_type = motion_types[0]
        current_anom = anomaly_flags[0]
        for i in range(1, len(lons)):
            if motion_types[i] != current_type or anomaly_flags[i] != current_anom:
                segment_lons = lons[start_idx:i]
                segment_lats = lats[start_idx:i]
                segment_alts = alts[start_idx:i]
                if current_anom:
                    color = anomaly_color_map.get(current_type, "red")
                else:
                    color = color_map.get(current_type, "red")
                if len(segment_lons) > 1:
                    ax4.plot(segment_lons, segment_lats, segment_alts, linewidth=0.8, alpha=0.9, color=color)
                start_idx = i
                current_type = motion_types[i]
                current_anom = anomaly_flags[i]

        segment_lons = lons[start_idx:]
        segment_lats = lats[start_idx:]
        segment_alts = alts[start_idx:]
        if current_anom:
            color = anomaly_color_map.get(current_type, "red")
        else:
            color = color_map.get(current_type, "red")
        if len(segment_lons) > 1:
            ax4.plot(segment_lons, segment_lats, segment_alts, linewidth=0.8, alpha=0.9, color=color)

        for mt in color_map.keys():
            xs = [lon for lon, m, a in zip(lons, motion_types, anomaly_flags) if m == mt and not a]
            ys = [lat for lat, m, a in zip(lats, motion_types, anomaly_flags) if m == mt and not a]
            zs = [alt for alt, m, a in zip(alts, motion_types, anomaly_flags) if m == mt and not a]
            if xs:
                ax4.scatter(xs, ys, zs, s=4, alpha=0.6, color=color_map[mt])
            xs_a = [lon for lon, m, a in zip(lons, motion_types, anomaly_flags) if m == mt and a]
            ys_a = [lat for lat, m, a in zip(lats, motion_types, anomaly_flags) if m == mt and a]
            zs_a = [alt for alt, m, a in zip(alts, motion_types, anomaly_flags) if m == mt and a]
            if xs_a:
                ax4.scatter(xs_a, ys_a, zs_a, s=6, alpha=0.85, color=anomaly_color_map[mt])
    ax4.set_xlabel("Longitude (deg)")
    ax4.set_ylabel("Latitude (deg)")
    ax4.set_zlabel("Altitude (m)")
    ax4.set_title("3D Lon/Lat/Alt")
    _plot_hubs(ax4, hubs or [], "3d", color="black")

    fig.suptitle(title, fontsize=14)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    plt.show()


def main():
    args = parse_args()

    # Resolve path relative to node-simulator directory regardless of CWD
    project_root = Path(__file__).resolve().parents[1]
    json_path = (project_root / args.filename).resolve()

    try:
        lats, lons, alts, motion_types, anomaly_flags = load_lat_lon(json_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
        return

    hubs = []
    if args.hubs:
        hub_path = (project_root / args.hubs).resolve()
        try:
            hubs = load_hubs_from_route(hub_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: could not load hubs from {args.hubs}: {e}")

    title = f"GPS track from {json_path.name}"
    plot_views(lats, lons, alts, motion_types, anomaly_flags, title, hubs=hubs)


if __name__ == "__main__":
    main()

