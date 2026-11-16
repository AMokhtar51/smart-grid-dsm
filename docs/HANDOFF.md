# Handoff: Team 2 (GA/MA) & Team 3 (Simulation & Results)

Read this plus docs/CONTRACT.md (frozen interface). Run everything from the
repo root. Split 1 gives you working data, config, and a tested evaluator —
you never touch the constraint internals.

## The problem in one paragraph

10 jobs must each start somewhere inside their allowed window in a 24-slot
(hourly) day. A **chromosome = list of 10 start slots**. Electricity cost and
peak grid import depend on when jobs run (prices vary by hour, solar offsets
load midday). The evaluator already handles windows, chunk overlaps, the
household cap, and penalties — your GA only has to evolve start slots.

## Try it in 60 seconds (no implementation needed)

```python
from src.optimization import config, evaluator

chrom = evaluator.baseline_chromosome()   # valid schedule: list of 10 ints
res = evaluator.evaluate(chrom, scenario="tou")
print(res["feasible"], res["cost"], res["peak"])
print(res["net_import"])                  # 24 grid-import kW values
```

## Team 2: what you implement

| File | What goes in it |
|---|---|
| `src/optimization/ga.py` | `run_ga(seed)` — population, tournament selection, crossover, mutation. Full recipe in the file docstring. |
| `src/optimization/solver_config.py` | Only if you need to retune: population, rates, budget, weights. |

Facts you need:
- Gene i bounds: `config.JOBS[i]["earliest_start"]` .. `["latest_start"]` inclusive.
- Fitness: `evaluator.evaluate(chrom, scenario="tou")["objective"]` — lower is better.
- Budget: `config.EVALUATION_BUDGET` evaluations; `evaluator.reset_eval_count()` / `eval_count()` track them.
- Compare GA vs MA over `config.SEEDS` (30) with the same budget.

Result dict from `evaluate`: `feasible, violations, cost, peak, penalty,
objective, net_import (24 slots), load_profile (24 slots)`.

## Team 3: what you implement

| File | What goes in it |
|---|---|
| `src/optimization/memetic.py` | `local_search(chrom)` + `run_memetic(seed)` — GA plus gene-shift hill climbing. Recipe in the docstring. |
| `src/results/simulate.py` | `plot_profiles` (before/after load-profile figure) and `save_report` (comparative markdown: cost savings + peak shaving). The numeric wrappers are already done. |
| `src/results/run_experiments.py` | The seed loop comparing GA vs MA, saving summaries and the final report to `results/`. |

The two numbers your report is about:
- **Cost savings**: `evaluator.savings(chrom)["cost_savings_pct"]`
- **Peak shaving**: `evaluator.savings(chrom)["peak_savings_pct"]`
- Profiles to plot: `evaluator.before_after_profiles(chrom)["baseline"]` vs
  `["optimized"]` — two 24-value lists, one chart.

matplotlib is already in requirements.txt. Output goes to `results/`.

## Definition of done

- Team 2: `python -m src.results.run_experiments` runs 30 seeds x GA algorithm
  within budget and writes a comparison summary to `results/`.
- Team 3: `python -m src.results.run_experiments` runs 30 seeds x MA algorithm
  within budget and writes a comparison summary to `results/`.
  `results/` contains the before/after profile figure and a report
  showing cost savings % and peak shaving % for the best schedule.
- `python tests/test_contract.py` still passes (goldens may be updated only if
  config/data changed — never by editing the test to match broken code).
