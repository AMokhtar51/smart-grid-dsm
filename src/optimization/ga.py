"""Genetic algorithm stub (optimizer team - implement this file).

The problem in one line: for each of the 10 jobs in config.JOBS, pick a start
slot inside its allowed window so that electricity cost and peak import are
minimised and no rules are broken.

A chromosome is just a list of 10 ints: chromosome[i] = start slot of job i.
Allowed range for gene i: config.JOBS[i]["earliest_start"] .. ["latest_start"]
(inclusive). A valid example: evaluator.baseline_chromosome().

Recipe:
1. from src.optimization import config, evaluator
2. Seed a population of config.POPULATION_SIZE chromosomes: for each gene,
   sample a uniform random int in [earliest_start, latest_start] using
   random.Random(seed) so runs are reproducible.
3. Fitness = evaluator.evaluate(chrom, scenario="tou")["objective"].
   Lower is better. The penalty for broken windows/overlaps/household cap is
   already inside the objective - never check feasibility yourself.
4. Evolve with the knobs in src/optimization/solver_config.py
   (TOURNAMENT_SIZE, ELITISM, CROSSOVER_RATE, MUTATION_RATE):
   - selection: pick TOURNAMENT_SIZE random individuals, keep the best
   - crossover: swap genes between two parents with probability CROSSOVER_RATE
   - mutation: with probability MUTATION_RATE per gene, resample that gene
     uniformly in its bounds
   - after crossover/mutation, clamp every gene into its bounds
   - copy the best ELITISM individuals through unchanged
5. Stop after config.EVALUATION_BUDGET evaluations. evaluator.eval_count()
   counts them; call evaluator.reset_eval_count() before each run.
6. Return the dict described below (run_experiments.py depends on these keys).

Expected interface:
- run_ga(seed: int, budget: int | None = None) -> dict with keys
  "best_chromosome" (list[int]), "best_result" (evaluator.evaluate dict),
  "evaluations_used" (int).
"""


def run_ga(seed, budget=None):
    raise NotImplementedError("GA not implemented in Split 1")
