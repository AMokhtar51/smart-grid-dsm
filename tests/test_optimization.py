import random
from src.optimization.operators import clamp, crossover, mutate
from src.optimization import config
from src.optimization.ga import run_ga

# Clamp Tests

def test_clamp_inside_bounds():
    chromosome = [3, 5, 7]
    bounds = [(1, 5), (2, 8), (4, 9)]

    result = clamp(chromosome, bounds)

    assert result == [3, 5, 7]


def test_clamp_outside_bounds():
    chromosome = [0, 10, 15]
    bounds = [(1, 5), (2, 8), (4, 9)]

    result = clamp(chromosome, bounds)

    assert result == [1, 8, 9]


def test_clamp_invalid_length():
    chromosome = [1, 2]
    bounds = [(0, 5)]

    try:
        clamp(chromosome, bounds)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_clamp_invalid_bounds():
    chromosome = [3]
    bounds = [(5, 1)]

    try:
        clamp(chromosome, bounds)
        assert False, "Expected ValueError"
    except ValueError:
        pass


# Crossover Tests

def test_crossover_rate_zero():
    parent1 = [1, 2, 3, 4]
    parent2 = [5, 6, 7, 8]

    child1, child2 = crossover(
        parent1, parent2, 0, random.Random(42)
    )

    assert child1 == parent1
    assert child2 == parent2


def test_crossover_produces_children():
    parent1 = [1, 2, 3, 4]
    parent2 = [5, 6, 7, 8]

    child1, child2 = crossover(
        parent1, parent2, 1, random.Random(42)
    )

    assert len(child1) == len(parent1)
    assert len(child2) == len(parent2)

    assert child1 != parent1
    assert child2 != parent2


def test_crossover_invalid_length():
    parent1 = [1, 2]
    parent2 = [3, 4, 5]

    try:
        crossover(parent1, parent2, 1, random.Random(42))
        assert False, "Expected ValueError"
    except ValueError:
        pass

# Mutation Tests

def test_mutation_rate_zero():
    chromosome = [3, 5, 7]
    bounds = [(1, 5), (2, 8), (4, 9)]

    result = mutate(
        chromosome, bounds, 0, random.Random(42)
    )

    assert result == chromosome


def test_mutation_respects_bounds():
    chromosome = [3, 5, 7]
    bounds = [(1, 5), (2, 8), (4, 9)]

    result = mutate(
        chromosome, bounds, 1, random.Random(42)
    )

    assert len(result) == len(bounds)

    for gene, (low, high) in zip(result, bounds):
        assert low <= gene <= high


def test_mutation_invalid_length():
    chromosome = [1, 2]
    bounds = [(0, 5)]

    try:
        mutate(chromosome, bounds, 1, random.Random(42))
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_mutation_invalid_bounds():
    chromosome = [3]
    bounds = [(5, 1)]

    try:
        mutate(chromosome, bounds, 1, random.Random(42))
        assert False, "Expected ValueError"
    except ValueError:
        pass

# GA Integration Tests

def test_ga_runs_successfully():
    result = run_ga(seed=42, budget=50)

    assert result["best_chromosome"] is not None
    assert result["best_result"] is not None
    assert result["evaluations_used"] == 50


def test_ga_reproducibility():
    result1 = run_ga(seed=42, budget=50)
    result2 = run_ga(seed=42, budget=50)

    assert result1["best_chromosome"] == result2["best_chromosome"]

    assert (
        result1["best_result"]["objective"]
        == result2["best_result"]["objective"]
    )


def test_ga_best_chromosome_respects_bounds():
    result = run_ga(seed=42, budget=50)

    bounds = [
        (job["earliest_start"], job["latest_start"])
        for job in config.JOBS
    ]

    chromosome = result["best_chromosome"]

    assert len(chromosome) == len(bounds)

    for gene, (low, high) in zip(chromosome, bounds):
        assert low <= gene <= high
