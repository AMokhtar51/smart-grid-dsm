# Smart Grid DSM v2 - Frozen Contract

## Conventions
- Hour h = [h, h+1). Slot 0 = 00:00. Single day, no midnight wrap.
- earliest_start = first allowed start slot. latest_end is EXCLUSIVE.
- A job starting at s needs s + duration <= latest_end.
- Net grid import per slot = max(0, appliance load + base load - solar) (curtailed surplus).
- Cost = sum(net import x price). Peak = max net import (kW).

## Sources of truth
- Appliances: `data/processed/appliances.json` (derived from REFIT House 2,
  Zenodo 5063428; unmonitored appliances marked "assumed": true).
- Prices: `config/pricing.json` (off_peak 0.5 for 0-6, standard 1.0 for 6-17,
  peak 2.0 for 17-22, standard 1.0 for 22-24).
- Optimization config: `src/optimization/config.py` (JOBS, scenarios, solar,
  base load, weights). Constraints API: `src/constraints` (Appliance,
  load_appliances, load_pricing, PricingTiers.price_at/price_vector).

## Appliance schema (v2, grounded in REFIT House 2)
| appliance | power_kw | duration_slots | interruptible | source |
|---|---|---|---|---|
| washing_machine | 0.369 | 2 | yes (1-slot chunks) | REFIT, 350 cycles |
| dishwasher | 0.747 | 2 | yes (1-slot chunks) | REFIT, 487 cycles |
| ev_charger | 7.0 | 4 | yes (1-slot chunks) | assumed (not monitored in House 2) |
| water_heater | 2.0 | 2 | yes (1-slot chunks) | assumed (not monitored in House 2) |

power_kw = median cycle mean draw; duration = median cycle length rounded to
hourly slots; interruptible = >= 30% of cycles contain a pause.

## Chromosome
- List[int] of length config.N_GENES (10 in v2). One gene per job in
  config.JOBS (flat list). Each gene is a start slot.
- Bounds per gene: [job["earliest_start"], job["latest_start"]] inclusive.
- Interruptible appliances split into 1-slot chunks; chunks must not overlap.

## JOBS (v2)
| id | appliance | power_kw | duration_h | earliest_start | latest_start |
|---|---|---|---|---|---|
| washing_machine_0/1 | washing_machine | 0.369 | 1 | 8 | 21 |
| dishwasher_0/1 | dishwasher | 0.747 | 1 | 12 | 22 |
| ev_charger_0..3 | ev_charger | 7.0 | 1 | 0 | 8 |
| water_heater_0/1 | water_heater | 2.0 | 1 | 5 | 21 |

## Evaluator (`from src.optimization import evaluator`)
- evaluator.evaluate(chromosome, prices=None, scenario=None, use_solar=None, use_base_load=None) -> dict
  keys: feasible, violations, cost, peak, penalty, objective, components, net_import, load_profile
- evaluator.baseline_chromosome() -> list[int]
- evaluator.load_profile(chromosome) -> list[float] (appliance load per slot)
- evaluator.net_profile(...), evaluator.before_after_profiles(...)
- evaluator.savings(chromosome, ...) -> dict with baseline/optimized cost, peak, savings %
- evaluator.reset_eval_count(), evaluator.eval_count()

## Scenarios
- "flat", "tou" (from config/pricing.json), "spiky" (seeded).

## Source notes
- REFIT dataset: Murray et al., Sci. Data 4:160122 (2017), CC BY 4.0.
- EV charger / water heater values are hand-set and should be replaced when a
  monitored source is available.
