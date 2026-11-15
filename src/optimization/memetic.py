"""Memetic algorithm stub (optimizer team).

Local search shifts each gene by at most config.LOCAL_SEARCH_MAX_SHIFT toward
solar peaks or price dips, then evaluates with evaluator.evaluate.

Expected interface:
- local_search(chromosome, budget=None) -> chromosome
- run_memetic(seed, budget=None) -> dict with keys
  "best_chromosome", "best_result", "evaluations_used".
"""


def local_search(chromosome, budget=None):
    raise NotImplementedError("Memetic local search not implemented in Split 1")


def run_memetic(seed, budget=None):
    raise NotImplementedError("Memetic algorithm not implemented in Split 1")