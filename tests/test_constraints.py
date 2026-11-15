import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constraints import (
    Appliance,
    PricingTiers,
    SLOTS_PER_DAY,
    load_appliances,
    load_pricing,
    validate_slot,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _wm(**over):
    d = {
        "name": "washing_machine",
        "power_kw": 1.0,
        "duration_slots": 2,
        "interruptible": False,
        "earliest_start": 8,
        "latest_end": 22,
    }
    d.update(over)
    return d


def _ev(**over):
    d = {
        "name": "ev_charger",
        "power_kw": 7.0,
        "duration_slots": 4,
        "interruptible": True,
        "earliest_start": 0,
        "latest_end": 9,
        "min_run_slots": 2,
    }
    d.update(over)
    return d


def _expect_value_error(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError(f"{label}: expected ValueError")


# --- Appliance schema -------------------------------------------------------


def test_accepts_valid_appliance():
    a = Appliance(**_wm())
    assert a.name == "washing_machine" and a.min_run_slots is None
    assert Appliance(**_ev()).min_run_slots == 2


def test_rejects_non_positive_power_and_duration():
    for bad in (0.0, -1.0):
        _expect_value_error(lambda: Appliance(**_wm(power_kw=bad)), "power %r" % bad)
    for bad in (0, -3):
        _expect_value_error(
            lambda: Appliance(**_wm(duration_slots=bad)), "duration %r" % bad
        )


def test_rejects_window_too_short_for_duration():
    _expect_value_error(
        lambda: Appliance(**_wm(earliest_start=8, latest_end=10, duration_slots=3)),
        "window shorter than duration",
    )


def test_rejects_bad_windows():
    _expect_value_error(lambda: Appliance(**_wm(earliest_start=25)), "start beyond day")
    _expect_value_error(
        lambda: Appliance(**_wm(latest_end=23, earliest_start=23)), "empty window"
    )


def test_rejects_bad_min_run_slots():
    _expect_value_error(
        lambda: Appliance(**_wm(min_run_slots=1)), "min_run_slots on non-interruptible"
    )
    _expect_value_error(lambda: Appliance(**_ev(min_run_slots=0)), "zero min_run_slots")
    _expect_value_error(
        lambda: Appliance(**_ev(min_run_slots=5)), "min_run_slots > duration"
    )


# --- Pricing tiers ----------------------------------------------------------


def test_price_at_tier_boundaries():
    p = load_pricing()
    assert p.price_at(0) == 0.5
    assert p.price_at(5) == 0.5  # last off-peak slot
    assert p.price_at(6) == 1.0  # first standard slot
    assert p.price_at(16) == 1.0
    assert p.price_at(17) == 2.0  # first peak slot
    assert p.price_at(21) == 2.0  # last peak slot
    assert p.price_at(22) == 1.0
    assert p.price_at(23) == 1.0


def test_price_at_out_of_range():
    p = load_pricing()
    _expect_value_error(lambda: p.price_at(SLOTS_PER_DAY), "slot == day")
    _expect_value_error(lambda: p.price_at(-1), "negative slot")


def test_price_vector_matches_price_at():
    p = load_pricing()
    vec = p.price_vector()
    assert len(vec) == SLOTS_PER_DAY
    assert all(vec[s] == p.price_at(s) for s in range(SLOTS_PER_DAY))


def _tiers(*tiers):
    return {
        "slots_per_day": SLOTS_PER_DAY,
        "tiers": [
            {"name": n, "start_hour": s, "end_hour": e, "price_per_kwh": v}
            for n, s, e, v in tiers
        ],
    }


def test_rejects_tier_gap():
    _expect_value_error(
        lambda: PricingTiers.from_config(_tiers(("a", 0, 6, 0.5), ("b", 7, 24, 1.0))),
        "gap",
    )


def test_rejects_tier_overlap():
    _expect_value_error(
        lambda: PricingTiers.from_config(_tiers(("a", 0, 6, 0.5), ("b", 5, 24, 1.0))),
        "overlap",
    )


def test_rejects_incomplete_coverage():
    _expect_value_error(
        lambda: PricingTiers.from_config(_tiers(("a", 0, 6, 0.5), ("b", 6, 23, 1.0))),
        "incomplete",
    )


def test_rejects_negative_price():
    _expect_value_error(
        lambda: PricingTiers.from_config(_tiers(("a", 0, 24, -1.0))), "negative price"
    )


# --- Time grid --------------------------------------------------------------


def test_validate_slot():
    assert (
        validate_slot(0) == 0 and validate_slot(SLOTS_PER_DAY - 1) == SLOTS_PER_DAY - 1
    )
    _expect_value_error(lambda: validate_slot(SLOTS_PER_DAY), "slot == day")


# --- Loader round trip ------------------------------------------------------


def test_load_appliances_round_trip():
    apps = load_appliances()
    assert apps and all(isinstance(a, Appliance) for a in apps)
    assert len({a.name for a in apps}) == len(apps)
    for a in apps:
        assert Appliance.from_dict(a.to_dict()) == a


def test_load_pricing_round_trip():
    p = load_pricing()
    assert PricingTiers.from_config(p.to_dict()) == p


def test_load_appliances_missing_file_message():
    try:
        load_appliances(os.path.join(REPO, "data", "processed", "does_not_exist.json"))
    except FileNotFoundError as e:
        assert "python -m src.data.collect" in str(e)
    else:
        raise AssertionError("expected FileNotFoundError")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print("ALL PASS")
