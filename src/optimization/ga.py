"""Genetic algorithm stub (optimizer team).

Responsibilities:
- Evolve a population of chromosomes (list[int] of length config.N_GENES).
- Each gene is a start slot bounded by the corresponding config.JOBS entry.
- Use evaluator.evaluate for fitness (minimise objective).
- Respect config.EVALUATION_BUDGET as the total number of evaluations.

Expected interface:
- run_ga(seed: int, budget: int | None = None) -> dict with keys
  "best_chromosome", "best_result", "evaluations_used".
"""


def run_ga(seed, budget=None):
    raise NotImplementedError("GA not implemented in Split 1")