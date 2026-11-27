import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constraints import Appliance, PricingTiers
from src.optimization import config, evaluator


def test_golden_flags_off_tou():
    old_s, old_b = config.USE_SOLAR, config.USE_BASE_LOAD
    try:
        config.USE_SOLAR = False
        config.USE_BASE_LOAD = False
        chrom = evaluator.baseline_chromosome()
        r = evaluator.evaluate(chrom, scenario="tou")
        assert r["cost"] == 36.964, r["cost"]
        assert r["peak"] == 7.0, r["peak"]
        assert r["feasible"] is True
    finally:
        config.USE_SOLAR = old_s
        config.USE_BASE_LOAD = old_b


def test_golden_flags_on_scenarios():
    chrom = evaluator.baseline_chromosome()
    expected = {"flat": 38.832, "tou": 41.764, "spiky": 48.752}
    for scen, cost in expected.items():
        r = evaluator.evaluate(chrom, scenario=scen)
        assert abs(r["cost"] - cost) < 1e-9, (scen, r["cost"])
        assert r["peak"] == 7.5, (scen, r["peak"])
        assert r["feasible"] is True


def test_out_of_window_violations():
    chrom = evaluator.baseline_chromosome()
    # ev chunks are genes 4..7 (window ends at 9)
    chrom[4] = 10
    r = evaluator.evaluate(chrom, scenario="tou")
    assert r["violations"] > 0
    feasible_chrom = evaluator.baseline_chromosome()
    r0 = evaluator.evaluate(feasible_chrom, scenario="tou")
    assert r["objective"] > r0["objective"]


def test_overlapping_chunks():
    chrom = evaluator.baseline_chromosome()
    # overlap two ev chunks
    chrom[4] = 5
    chrom[5] = 5
    r = evaluator.evaluate(chrom, scenario="tou")
    assert r["violations"] > 0


def test_wrong_chromosome_length():
    try:
        evaluator.evaluate([0, 1, 2], scenario="tou")
        raise AssertionError("wrong length not rejected")
    except ValueError:
        pass


def test_bad_constraints_rejected():
    # window too short for duration
    try:
        Appliance(name="wm", power_kw=1.0, duration_slots=3, earliest_start=8, latest_end=10)
        raise AssertionError("bad window accepted")
    except ValueError:
        pass
    # pricing tier gap
    cfg = {"tiers": [
        {"name": "a", "start_hour": 0, "end_hour": 6, "price_per_kwh": 0.5},
        {"name": "b", "start_hour": 7, "end_hour": 24, "price_per_kwh": 1.0},
    ]}
    try:
        PricingTiers.from_config(cfg)
        raise AssertionError("tier gap accepted")
    except ValueError:
        pass


def test_random_feasible_chromosome():
    import random

    rng = random.Random(7)
    chrom = [rng.randrange(config.JOBS[i]["earliest_start"], config.JOBS[i]["latest_start"] + 1)
             for i in range(config.N_GENES)]
    r = evaluator.evaluate(chrom, scenario="flat")
    assert all(isinstance(x, (int, float)) and x == x for x in [r["cost"], r["peak"], r["objective"]])
    assert len(r["net_import"]) == config.SLOTS_PER_DAY
    assert len(r["load_profile"]) == config.SLOTS_PER_DAY


def test_baseline_chromosome_length():
    assert len(evaluator.baseline_chromosome()) == config.N_GENES


def test_household_limit_violation():
    chrom = evaluator.baseline_chromosome()

    old_limit = config.HOUSEHOLD_LIMIT_KW
    try:
        config.HOUSEHOLD_LIMIT_KW = 1.0

        r = evaluator.evaluate(chrom, scenario="tou")

        assert r["violations"] > 0
        assert r["feasible"] is False
    finally:
        config.HOUSEHOLD_LIMIT_KW = old_limit

def test_penalty_applied_for_violations():
    chrom = evaluator.baseline_chromosome()

    valid = evaluator.evaluate(chrom, scenario="tou")

    invalid_chrom = chrom.copy()
    invalid_chrom[4] = 10

    invalid = evaluator.evaluate(invalid_chrom, scenario="tou")

    assert invalid["penalty"] > valid["penalty"]
    assert invalid["objective"] > valid["objective"]

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print("ALL PASS")
