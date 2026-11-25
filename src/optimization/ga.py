import operator
import random

from src.optimization import config, evaluator
from src.optimization.operators import clamp, crossover, mutate


def _to_int(value):
    if isinstance(value, bool):
        raise TypeError("Gene value cannot be a boolean")
    return operator.index(value)


def _init_population(pop_size, bounds, rng):
    population = []
    for _ in range(pop_size):
        chrom = [rng.randint(low, high) for low, high in bounds]
        population.append(chrom)
    return population


def _tournament_select(evaluated_pop, tournament_size, rng):
    k = min(tournament_size, len(evaluated_pop))
    competitors = rng.sample(evaluated_pop, k)
    winner, _ = min(competitors, key=lambda item: item[1]["objective"])
    return list(winner)


def run_ga(seed: int, budget: int | None = None) -> dict:
    """Run the Genetic Algorithm for a given seed and evaluation budget."""
    rng = random.Random(seed)
    evaluator.reset_eval_count()

    pop_size = config.POPULATION_SIZE
    max_evals = config.EVALUATION_BUDGET if budget is None else budget
    tournament_size = config.TOURNAMENT_SIZE
    elitism = config.ELITISM
    crossover_rate = config.CROSSOVER_RATE
    mutation_rate = config.MUTATION_RATE

    if pop_size < 1:
        raise ValueError("POPULATION_SIZE must be at least 1")
    if max_evals < 1:
        raise ValueError("Evaluation budget must be at least 1")
    if tournament_size < 1:
        raise ValueError("TOURNAMENT_SIZE must be at least 1")
    if not (0 <= elitism < pop_size):
        raise ValueError("ELITISM must satisfy 0 <= ELITISM < POPULATION_SIZE")

    bounds = [(job["earliest_start"], job["latest_start"]) for job in config.JOBS]

    # Seed and evaluate initial population
    initial_pop = _init_population(pop_size, bounds, rng)
    evaluated_pop = []
    best_chrom = None
    best_result = None

    for chrom in initial_pop:
        if evaluator.eval_count() >= max_evals:
            break
        res = evaluator.evaluate(chrom, scenario="tou")
        evaluated_pop.append((chrom, res))
        if best_result is None or res["objective"] < best_result["objective"]:
            best_chrom = list(chrom)
            best_result = res

    if not evaluated_pop or best_chrom is None:
        raise ValueError("Initial population evaluation failed")

    # Evolve generations until budget is exhausted
    while evaluator.eval_count() < max_evals:
        evaluated_pop.sort(key=lambda item: item[1]["objective"])

        n_elites = min(elitism, len(evaluated_pop))
        next_pop = [(list(chrom), res) for chrom, res in evaluated_pop[:n_elites]]

        while len(next_pop) < pop_size and evaluator.eval_count() < max_evals:
            parent1 = _tournament_select(evaluated_pop, tournament_size, rng)
            parent2 = _tournament_select(evaluated_pop, tournament_size, rng)

            child1, child2 = crossover(parent1, parent2, crossover_rate, rng)

            for child in (child1, child2):
                if len(next_pop) >= pop_size or evaluator.eval_count() >= max_evals:
                    break
                child = mutate(child, bounds, mutation_rate, rng)
                child = [_to_int(g) for g in clamp(child, bounds)]

                res = evaluator.evaluate(child, scenario="tou")
                next_pop.append((child, res))
                if res["objective"] < best_result["objective"]:
                    best_chrom = list(child)
                    best_result = res

        evaluated_pop = next_pop

    return {
        "best_chromosome": list(best_chrom),
        "best_result": best_result,
        "evaluations_used": evaluator.eval_count(),
    }