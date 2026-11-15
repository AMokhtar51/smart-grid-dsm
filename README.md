# Smart Grid Energy Demand Side Management

Constraint modelling for household appliance scheduling under dynamic
electricity pricing. Split 1 owns the **constraints** package (appliance
profiles + pricing tiers) and the data collection that grounds them; the
optimizer and results teams consume its output.

## What other teams import

```python
from src.constraints import Appliance, load_appliances, load_pricing, SLOTS_PER_DAY

appliances = load_appliances()      # list[Appliance]
pricing = load_pricing()            # PricingTiers
price = pricing.price_at(18)        # price for one slot (0..23)
vector = pricing.price_vector()     # full 24-slot price vector
```

The optimizer team additionally uses `src/optimization/config.py` (JOBS,
N_GENES, scenarios, solar/base load) and `src/optimization/evaluator.py`
(frozen v1 contract, see `docs/CONTRACT.md`).

Run everything from the repo root (or set `PYTHONPATH` to it); packages live
under `src/`.

## Structure

- `config/pricing.json` - ToU tiers (off-peak / standard / peak), start/end
  hours, price per kWh.
- `data/processed/appliances.json` - appliance profiles (power, duration,
  interruptibility) derived from REFIT House 2; unmonitored appliances are
  marked `"assumed": true`.
- `src/constraints/` - `Appliance` model, `PricingTiers` (`price_at`,
  `price_vector`), shared `SLOTS_PER_DAY` grid, loaders.
- `src/data/collect.py` - downloads REFIT and derives the appliance profiles.
- `src/optimization/` - optimizer team (config, evaluator, GA/MA stubs).
- `src/results/` - results team stubs.
- `tests/` - `test_constraints.py` (schema, tier boundaries, loader) and
  `test_contract.py` (frozen evaluator contract).

## Running

```sh
python -m src.data.collect      # rebuild data/processed/appliances.json (downloads REFIT House 2 if needed)
python tests/test_constraints.py
python tests/test_contract.py
```

Split 1 code is standard library only.

## Dataset

Appliance profiles are derived from the REFIT Electrical Load Measurements
(cleaned) dataset, Zenodo record 5063428, House 2, CC BY 4.0
(https://zenodo.org/records/5063428). The raw CSV (~325 MB) is stored in
`data/raw/` which is gitignored; `collect.py` re-downloads it if missing.
House 2 does not monitor an EV charger or water heater, so those entries keep
documented hand-set values marked `"assumed": true` in the JSON.

## Conventions

- 24 hourly slots per day, slot 0 = 00:00, no midnight wrap.
- `earliest_start` = first allowed start slot; `latest_end` is EXCLUSIVE.
- Units: power kW, prices relative units per kWh.
