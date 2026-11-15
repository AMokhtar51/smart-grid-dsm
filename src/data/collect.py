"""Derive appliance profiles from the REFIT public dataset (CC BY 4.0).

Downloads one house's cleaned CSV from the REFIT Electrical Load Measurements
dataset (Zenodo record 5063428), detects appliance ON-cycles, and derives
typical power draw, run duration, and interruptibility per appliance. Results
are written to data/processed/appliances.json.

Appliances not present in the chosen house (e.g. EV charger, water heater)
keep documented hand-set values, marked "assumed": true.

Usage:
    python -m src.data.collect [--house 2] [--redownload]
"""

import argparse
import csv
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw"
OUT_FILE = REPO_ROOT / "data" / "processed" / "appliances.json"
sys.path.insert(0, str(REPO_ROOT))

from src.constraints import Appliance, SLOTS_PER_DAY  # noqa: E402

ZENODO = "https://zenodo.org/records/5063428/files/CLEAN_House{i}.csv?download=1"

# IAM column -> appliance name, per house (REFIT ReadMe).
HOUSE_COLUMNS = {
    2: {1: "fridge_freezer", 2: "washing_machine", 3: "dishwasher",
        4: "television_site", 5: "microwave", 6: "toaster", 7: "hifi",
        8: "kettle", 9: "overhead_fan"},
    5: {1: "fridge_freezer", 2: "tumble_dryer", 3: "washing_machine",
        4: "dishwasher", 5: "desktop_computer", 6: "television_site",
        7: "microwave", 8: "kettle", 9: "toaster"},
}
SCHEDULABLE = {"washing_machine", "dishwasher", "tumble_dryer", "washer_dryer"}

ON_THRESHOLD_W = 20.0
MIN_EVENT_MINUTES = 10
MIN_PEAK_W = 50.0
GAP_TOLERANCE_MINUTES = 5
INTERRUPTIBLE_GAP_FRACTION = 0.3

# Windows follow the frozen v1 contract; the dataset grounds power, duration
# and interruptibility only.
CONTRACT_WINDOWS = {
    "washing_machine": (8, 22),
    "dishwasher": (12, 23),
    "tumble_dryer": (8, 22),
    "washer_dryer": (8, 22),
    "ev_charger": (0, 9),
    "water_heater": (5, 22),
}

# Hand-set values for appliances REFIT House 2 does not monitor.
ASSUMED = {
    "ev_charger": {"power_kw": 7.0, "duration_slots": 4, "interruptible": True},
    "water_heater": {"power_kw": 2.0, "duration_slots": 2, "interruptible": True},
}


def main():
    args = _parse_args()
    raw = RAW_DIR / ("CLEAN_House%d.csv" % args.house)
    if args.redownload or not raw.exists():
        _download(raw, args.house)
    profiles = _derive(raw, args.house)
    _write(profiles, args.house)
    print("wrote %s" % OUT_FILE)


def _parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--house", type=int, default=2, help="REFIT house number")
    p.add_argument("--redownload", action="store_true")
    return p.parse_args()


def _download(dest, house):
    url = ZENODO.format(i=house)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("downloading %s -> %s" % (url, dest))
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        done = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            print("\r%.0f MB" % (done / 1e6), end="", flush=True)
    print()
    tmp.replace(dest)


def _derive(raw, house):
    series = _to_minutes(raw, house)
    profiles = {}
    for alias, minutes in series.items():
        events = _events(minutes)
        if events:
            profiles[alias] = _profile(alias, events)
    for name, vals in ASSUMED.items():
        profiles.setdefault(name, dict(vals, assumed=True))
    return profiles


def _to_minutes(raw, house):
    """Stream the 8-second CSV into per-minute mean watts, aligned lists.

    A minute with no readable rows counts as 0 W (OFF). Rows are chronological;
    out-of-order rows are skipped.
    """
    tracked = {i: a for i, a in HOUSE_COLUMNS[house].items() if a in SCHEDULABLE}
    if not tracked:
        raise SystemExit("no schedulable appliances in REFIT House %d" % house)
    series = {a: [] for a in tracked.values()}
    buf = {a: [0.0, 0] for a in tracked.values()}
    base = None
    cur = None
    with open(raw, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            try:
                minute = int(float(row[1])) // 60
            except ValueError:
                continue
            if cur is None:
                cur = base = minute
            elif minute != cur:
                if minute < cur:
                    continue
                _flush(buf, series, cur, base)
                cur = minute
            for i, a in tracked.items():
                try:
                    w = float(row[2 + i])
                except (ValueError, IndexError):
                    continue
                if 0.0 <= w <= 4000.0:
                    buf[a][0] += w
                    buf[a][1] += 1
    if cur is not None:
        _flush(buf, series, cur, base)
    return series


def _flush(buf, series, minute, base):
    idx = minute - base
    for a, (total, n) in buf.items():
        mean = total / n if n else 0.0
        lst = series[a]
        while len(lst) < idx:
            lst.append(0.0)
        lst.append(mean)
        buf[a][0] = 0.0
        buf[a][1] = 0


def _events(minutes):
    """Split a per-minute series into ON events; gaps <= tolerance stay inside."""
    evs = []
    cur, gap = [], 0
    for w in minutes:
        if w >= ON_THRESHOLD_W:
            if cur and gap:
                cur.extend([0.0] * gap)
            cur.append(w)
            gap = 0
        elif cur:
            gap += 1
            if gap > GAP_TOLERANCE_MINUTES:
                _close(evs, cur)
                cur, gap = [], 0
    _close(evs, cur)
    return evs


def _close(evs, cur):
    if len(cur) >= MIN_EVENT_MINUTES and max(cur, default=0.0) >= MIN_PEAK_W:
        evs.append(cur)


def _profile(alias, events):
    cycle_means = sorted(sum(e) / len(e) for e in events)
    median_draw = cycle_means[len(cycle_means) // 2]
    lengths = sorted(len(e) for e in events)
    median_len = lengths[len(lengths) // 2]
    with_gaps = sum(1 for e in events if 0.0 in e)
    return {
        "power_kw": round(median_draw / 1000.0, 3),
        "duration_slots": max(1, round(median_len / 60.0)),
        "interruptible": with_gaps / len(events) >= INTERRUPTIBLE_GAP_FRACTION,
        "earliest_start": CONTRACT_WINDOWS[alias][0],
        "latest_end": CONTRACT_WINDOWS[alias][1],
        "assumed": False,
        "n_cycles": len(events),
    }


def _write(profiles, house):
    entries = []
    for name in sorted(profiles):
        p = profiles[name]
        earliest, latest = CONTRACT_WINDOWS[name]
        a = Appliance(
            name=name,
            power_kw=p["power_kw"],
            duration_slots=p["duration_slots"],
            interruptible=p["interruptible"],
            earliest_start=earliest,
            latest_end=latest,
        ).to_dict()
        a["assumed"] = p.get("assumed", False)
        if "n_cycles" in p:
            a["n_cycles"] = p["n_cycles"]
        entries.append(a)
    out = {
        "slots_per_day": SLOTS_PER_DAY,
        "source": "REFIT Electrical Load Measurements (cleaned), Zenodo 5063428, House %d, CC BY 4.0" % house,
        "appliances": entries,
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
