"""Memetic algorithm stub (optimizer team - implement this file).

Same problem, same chromosome, same fitness as ga.py (read its docstring
first). A memetic algorithm = GA + local search on the best individuals.

Recipe:
1. Run your GA as in ga.py, then polish with local_search - or apply
   local_search to the top few individuals every generation. Either is fine;
   the budget is what matters.
2. local_search: try shifting ONE gene at a time by -1..-LOCAL_SEARCH_MAX_SHIFT
   and +1..+LOCAL_SEARCH_MAX_SHIFT slots (clamped to the gene's bounds). If
   evaluator.evaluate says the objective improved, keep the shift and repeat
   from the new chromosome; otherwise try the next shift. Stop when no shift
   improves the objective.
3. Track the budget with evaluator.eval_count() (call
   evaluator.reset_eval_count() before each run) so GA + local search together
   stay within config.EVALUATION_BUDGET.
4. Return the same dict shape as run_ga.

Expected interface:
- local_search(chromosome, budget=None) -> improved chromosome
- run_memetic(seed, budget=None) -> dict with keys
  "best_chromosome", "best_result", "evaluations_used".
"""


def local_search(chromosome, budget=None):
    raise NotImplementedError("Memetic local search not implemented in Split 1")


def run_memetic(seed, budget=None):
    raise NotImplementedError("Memetic algorithm not implemented in Split 1")
