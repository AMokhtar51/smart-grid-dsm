"""Experiment runner stub (optimizer + results teams - implement this file).

Compares GA vs MA fairly across the same seeds, then hands results to team 3.

Recipe:
1. from src.optimization import config, evaluator
   from src.optimization import ga, memetic
   from src.results import simulate
2. For each seed in config.SEEDS (30 of them):
       evaluator.reset_eval_count()
       res_ga = ga.run_ga(seed)
       evaluator.reset_eval_count()
       res_ma = memetic.run_memetic(seed)
   Both algorithms get the same config.EVALUATION_BUDGET - resetting the
   counter before each run is what makes the comparison fair.
3. Collect res["best_result"]["objective"], ["cost"], ["peak"] per seed;
   report mean/std over the seeds for GA vs MA.
4. Pick the overall best chromosome and produce the final deliverables via
   simulate.plot_profiles(...) and simulate.save_report(...).
5. Save any summary table (CSV or markdown) to results/.

Expected interface:
- main() -> None; writes comparison summary + final report to results/.
"""


def main():
    raise NotImplementedError("Experiment runner not implemented in Split 1")


if __name__ == "__main__":
    main()
