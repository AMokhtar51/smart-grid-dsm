# Smart Grid Energy Load Balancing (DSM)

Smart-grid Demand Side Management: schedule shiftable home appliances over a 24-hour period to minimise electricity cost under dynamic time-of-use pricing and reduce peak grid load, while respecting appliance operating windows.

## Overview

This repository implements Phase 1 (Constraint Modelling): appliance profiles (power draw, duration, interruptible vs. uninterruptible cycles) and dynamic electricity pricing tiers. The optimisation algorithms (GA/MA) and simulation/reporting are downstream work that consume the constraints package in `src/constraints/`.

## Features

- Appliance profiles with power (kW), duration (hourly slots), interruptibility, and allowed time windows
- Dynamic pricing tiers covering all 24 hours, with gap/overlap/coverage validation
- Shared 24-slot day grid and slot validation
- Loaders for appliances and pricing, with round-trip serialisation
- REFIT House 2 data collection to derive appliance profiles (`src/data/collect.py`)
- Frozen evaluator contract and optimisation configuration for downstream teams

## Project structure

```
config/pricing.json              Time-of-use pricing tiers
data/processed/appliances.json   Appliance profiles consumed by all teams
data/raw/                        Raw REFIT CSV (gitignored; re-downloaded by collect.py)
docs/CONTRACT.md                 Frozen v2 contract and schema
docs/HANDOFF.md                  Handoff notes for GA/MA and results teams
src/constraints/                 Appliance model, pricing tiers, time grid, loaders
src/data/collect.py              Derives appliance profiles from REFIT House 2
src/optimization/                Config, evaluator, GA/MA stubs (downstream teams)
src/results/                     Simulation/reporting stubs (downstream teams)
tests/test_constraints.py        Constraint schema, tier, loader tests
tests/test_contract.py           Frozen evaluator contract tests
```

## Requirements

- Python 3.10+ (uses `int | None` type hints)
- Standard library only for the constraints package
- Optional: `numpy`, `pandas` (listed in `requirements.txt`; used by the notebook/downstream)
- Internet access and ~325 MB disk space to run `src/data/collect.py`

## Installation

```sh
git clone <repo-url>
cd smart-grid-dsm
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

- `config/pricing.json` — ToU tiers: `off_peak` 0.5 (0-6), `standard` 1.0 (6-17), `peak` 2.0 (17-22), `standard` 1.0 (22-24). Prices are relative units per kWh.
- `data/processed/appliances.json` — appliance profiles (`power_kw`, `duration_slots`, `interruptible`, `earliest_start`, `latest_end`, `assumed`, `n_cycles`).
- No environment variables are used.
- `data/raw/` is gitignored; `collect.py` re-downloads the REFIT CSV if missing.

## How to run

Rebuild appliance profiles (downloads REFIT House 2 if needed):

```sh
python -m src.data.collect
```

Run constraint tests:

```sh
python tests/test_constraints.py
```

Run frozen contract tests:

```sh
python tests/test_contract.py
```

Expected output for both test commands: `ALL PASS`.

Experiment runner (GA/MA comparison, simulation/reporting):

```sh
python -m src.results.run_experiments
```

TODO: confirm — this entry point is currently a stub (`NotImplementedError`) in this snapshot.

## Usage example

```python
from src.constraints import load_appliances, load_pricing, SLOTS_PER_DAY

appliances = load_appliances()      # list[Appliance]
pricing = load_pricing()            # PricingTiers
print(pricing.price_at(18))         # 2.0
print(pricing.price_vector())       # 24 prices
print([a.name for a in appliances])
```

## Testing

```sh
python tests/test_constraints.py
python tests/test_contract.py
```

## Troubleshooting

- `ModuleNotFoundError: No module named 'src'`: run commands from the repository root, or set `PYTHONPATH` to the repo root.
- `FileNotFoundError ... appliances.json`: run `python -m src.data.collect` to generate it.
- `collect.py` downloads ~325 MB and may take several minutes; ensure network access and disk space.
- Syntax errors on Python < 3.10: upgrade to Python 3.10+.
- `python -m src.results.run_experiments` raises `NotImplementedError`: GA/MA and results modules are not implemented yet.

## Contributors and License

- Contributors: TODO: confirm
- License: TODO: confirm (no license file present in the repository)