#!/usr/bin/env python3
"""Lanelet2 .osm -> .pcd (x y z intensity), e.g. to view the map in CloudCompare.

Every way (linestring) is sampled at a fixed step (default 0.1 m), the intensity
depends on the line type. Coordinates are the local_x / local_y / ele tags.

    python3 lanelet2pcd.py map.osm                 # -> map.pcd (map_1.pcd if it exists)
    python3 lanelet2pcd.py map.osm -s 0.25 --centerline
"""
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

# intensity per line type; first match wins: "type/subtype", then "type", then DEFAULT
INTENSITY = {
    "line_thin/solid": 100,
    "line_thin/dashed": 80,
    "line_thin": 90,
    "line_thick": 120,
    "road_border": 60,
    "curbstone": 60,
    "virtual": 20,
    "crosswalk": 160,       # bounds of crosswalk lanelets
    "road_shoulder": 50,    # bounds of road_shoulder lanelets
    "stop_line": 200,
    "traffic_sign": 220,
    "traffic_light": 240,
    "parking_lot": 40,
    "parking_space": 40,
    "centerline": 10,       # only with --centerline
}
DEFAULT_INTENSITY = 30
# lanelet subtypes that override the intensity of their bounding ways
LANELET_OVERRIDE = ("crosswalk", "road_shoulder")


def tags(elem):
    return {t.get("k"): t.get("v") for t in elem.findall("tag")}


def intensity_of(type_, subtype=None):
    for key in (f"{type_}/{subtype}", type_):
        if key in INTENSITY:
            return INTENSITY[key]
    return DEFAULT_INTENSITY


def resample(pts, step):
    """Points along the polyline `pts` (N x 3), `step` metres apart, ends included."""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate(([0.0], np.cumsum(seg)))
    if s[-1] <= 0:
        return pts[:1]
    n = max(int(np.ceil(s[-1] / step)), 1) + 1
    q = np.linspace(0.0, s[-1], n)
    return np.column_stack([np.interp(q, s, pts[:, i]) for i in range(3)])


def free_path(path):
    """`path` if it does not exist, otherwise the first free path_1, path_2, ..."""
    i, out = 0, path
    while out.exists():
        i += 1
        out = path.with_name(f"{path.stem}_{i}{path.suffix}")
    return out


def convert(osm, step, centerline):
    root = ET.parse(osm).getroot()

    nodes = {}
    for n in root.iter("node"):
        t = tags(n)
        if "local_x" in t and "local_y" in t:
            nodes[n.get("id")] = (float(t["local_x"]), float(t["local_y"]), float(t.get("ele") or 0))
    if not nodes:
        sys.exit("No local_x / local_y tags in the nodes - only local coordinates are supported.")

    ways, kind = {}, {}
    for w in root.iter("way"):
        pts = [nodes[r.get("ref")] for r in w.findall("nd") if r.get("ref") in nodes]
        if pts:
            t = tags(w)
            ways[w.get("id")] = np.array(pts)
            kind[w.get("id")] = intensity_of(t.get("type"), t.get("subtype"))

    clouds = []
    for rel in root.iter("relation"):
        t = tags(rel)
        if t.get("type") != "lanelet":
            continue
        bound = {m.get("role"): m.get("ref") for m in rel.findall("member") if m.get("type") == "way"}
        if t.get("subtype") in LANELET_OVERRIDE:
            for ref in (bound.get("left"), bound.get("right")):
                if ref in kind:
                    kind[ref] = intensity_of(t["subtype"])
        if centerline and bound.get("left") in ways and bound.get("right") in ways:
            left, right = ways[bound["left"]], ways[bound["right"]]
            n = max(len(left), len(right), 2) * 4
            u = np.linspace(0, 1, n)
            mid = (resample_n(left, u) + resample_n(right, u)) / 2
            clouds.append((resample(mid, step), INTENSITY["centerline"]))

    clouds += [(resample(p, step), kind[i]) for i, p in ways.items()]
    cloud = np.vstack([np.column_stack([p, np.full(len(p), v)]) for p, v in clouds]).astype(np.float32)
    # drop duplicates (shared end points, overlapping lines) on a step/2 grid
    _, keep = np.unique(np.round(cloud[:, :3] / (step / 2)).astype(np.int64), axis=0, return_index=True)
    return cloud[np.sort(keep)], len(ways)


def resample_n(pts, u):
    """Polyline `pts` evaluated at the normalised arc lengths `u` (0..1)."""
    s = np.concatenate(([0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))))
    s = s / s[-1] if s[-1] > 0 else np.linspace(0, 1, len(pts))
    return np.column_stack([np.interp(u, s, pts[:, i]) for i in range(3)])


def write_pcd(path, cloud):
    header = (
        "# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\n"
        "FIELDS x y z intensity\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\n"
        f"WIDTH {len(cloud)}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {len(cloud)}\nDATA binary\n"
    )
    with open(path, "wb") as f:
        f.write(header.encode("ascii"))
        f.write(cloud.astype("<f4").tobytes())


def main():
    ap = argparse.ArgumentParser(description="Lanelet2 .osm -> .pcd (x y z intensity)")
    ap.add_argument("osm", type=Path, help="lanelet2 .osm file")
    ap.add_argument("-s", "--step", type=float, default=0.1, help="point spacing along the lines [m] (default: 0.1)")
    ap.add_argument("-o", "--output", type=Path, help="output .pcd (default: next to the .osm, same name)")
    ap.add_argument("-c", "--centerline", action="store_true", help="also add the lanelet centerlines")
    ap.add_argument("-f", "--force", action="store_true", help="overwrite the output if it exists")
    a = ap.parse_args()
    if a.step <= 0:
        ap.error("--step must be positive")

    out = a.output or a.osm.with_suffix(".pcd")
    if not a.force:
        out = free_path(out)
    cloud, n_ways = convert(a.osm, a.step, a.centerline)
    write_pcd(out, cloud)
    print(f"{n_ways} lines -> {len(cloud)} points ({out.stat().st_size / 1e6:.2f} MB), step {a.step} m")
    values, counts = np.unique(cloud[:, 3], return_counts=True)
    names = {}
    for k, v in INTENSITY.items():
        names.setdefault(v, []).append(k)
    for v, c in zip(values, counts):
        print(f"  intensity {v:5.0f}: {c:8d} pts  {', '.join(names.get(int(v), ['other']))}")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
