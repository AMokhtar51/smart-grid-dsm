"""Optimization-side configuration, rebuilt on src.constraints.

Appliances and ToU prices come from data/processed/appliances.json and
config/pricing.json via the constraints module. This file keeps the frozen
v1 interface the evaluator and GA rely on: JOBS, N_GENES, PRICES,
PRICE_SCENARIOS, solar/base load, and solver weights.
"""

import random

from src.constraints import SLOTS_PER_DAY, load_appliances, load_pricing
from src.optimization.solver_config import *

# v1 gene order (frozen contract). Extra appliances, if any, follow sorted.
_ORDER = ["washing_machine", "dishwasher", "ev_charger", "water_heater"]


def _ordered(names):
    known = [n for n in _ORDER if n in names]
    return known + sorted(n for n in names if n not in _ORDER)


APPLIANCES = {a.name: a for a in load_appliances()}
for _n in _ordered(APPLIANCES):
    APPLIANCES[_n] = APPLIANCES.pop(_n)

# Baseline schedule (GA-team tunable): preferred start slot per appliance.
BASELINE_START = {
    "washing_machine": 18,
    "dishwasher": 20,
    "ev_charger": 5,
    "water_heater": 18,
}


def _build_jobs(appliances):
    jobs = []
    for name, a in appliances.items():
        if a.interruptible:
            chunk = a.min_run_slots or 1
            for i in range(a.duration_slots // chunk):
                jobs.append(
                    {
                        "id": f"{name}_{i}",  # noqa: UP031
                        "appliance": name,
                        "power_kw": a.power_kw,
                        "duration_h": chunk,
                        "earliest_start": a.earliest_start,
                        "latest_start": a.latest_end - chunk,
                    }
                )
        else:
            jobs.append(
                {
                    "id": name,
                    "appliance": name,
                    "power_kw": a.power_kw,
                    "duration_h": a.duration_slots,
                    "earliest_start": a.earliest_start,
                    "latest_start": a.latest_end - a.duration_slots,
                }
            )
    return jobs


# --- Pricing ----------------------------------------------------------------
_pricing = load_pricing()
PRICES = _pricing.price_vector()

_flat = [1.0] * SLOTS_PER_DAY

_rng = random.Random(42)
_spiky = list(PRICES)
for _h in _rng.sample(range(SLOTS_PER_DAY), 4):
    _spiky[_h] = PRICES[_h] * 3.0

PRICE_SCENARIOS = {
    "flat": _flat,
    "tou": PRICES,
    "spiky": _spiky,
}

# --- Solar / base load ------------------------------------------------------
SOLAR_BY_HOUR = {
    6: 0.3,
    7: 0.8,
    8: 1.5,
    9: 2.2,
    10: 2.8,
    11: 3.2,
    12: 3.4,
    13: 3.2,
    14: 2.8,
    15: 2.2,
    16: 1.5,
    17: 0.8,
    18: 0.3,
}
SOLAR_KW = [SOLAR_BY_HOUR.get(h, 0.0) for h in range(SLOTS_PER_DAY)]

BASE_LOAD_KW = [0.5] * SLOTS_PER_DAY

USE_SOLAR = True
USE_BASE_LOAD = True

# Optional household power cap (kW); violation if exceeded in any slot.
HOUSEHOLD_LIMIT_KW = 10.0


def _validate():
    for label, vals in (("SOLAR_KW", SOLAR_KW), ("BASE_LOAD_KW", BASE_LOAD_KW)):
        if len(vals) != SLOTS_PER_DAY:
            raise ValueError(f"{label} length must be {SLOTS_PER_DAY}")  # noqa: UP031
        for v in vals:
            if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                raise ValueError(f"{label} entries must be non-negative numbers")
    if HOUSEHOLD_LIMIT_KW is not None:  # noqa: SIM102
        if (
            not isinstance(HOUSEHOLD_LIMIT_KW, (int, float))
            or isinstance(HOUSEHOLD_LIMIT_KW, bool)
            or HOUSEHOLD_LIMIT_KW < 0
        ):
            raise ValueError("HOUSEHOLD_LIMIT_KW must be a non-negative number or None")


_validate()

JOBS = _build_jobs(APPLIANCES)
N_GENES = len(JOBS)
SEEDS = list(range(NUM_SEEDS))
