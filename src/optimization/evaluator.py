from src.optimization import config

_EVAL_COUNT = 0


def reset_eval_count():
    global _EVAL_COUNT
    _EVAL_COUNT = 0


def eval_count():
    return _EVAL_COUNT


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def jobs():
    return config.JOBS


def n_genes():
    return config.N_GENES


def baseline_chromosome():
    out = []
    for a_name, a in config.APPLIANCES.items():
        if a.interruptible:
            chunk = a.min_run_slots or 1
            k = a.duration_slots // chunk
            for i in range(k):
                out.append(config.BASELINE_START[a_name] + i * chunk)
        else:
            out.append(config.BASELINE_START[a_name])
    return out


def _job_at(i):
    return config.JOBS[i]


def _load_profile(chromosome):
    n = config.SLOTS_PER_DAY
    load = [0.0] * n
    for i, s in enumerate(chromosome):
        job = config.JOBS[i]
        if not _is_int(s):
            continue
        for d in range(job["duration_h"]):
            h = s + d
            if 0 <= h < n:
                load[h] += job["power_kw"]
    return load


def _violations(chromosome):
    v = 0
    if len(chromosome) != config.N_GENES:
        raise ValueError(f"chromosome length {len(chromosome)} != {config.N_GENES}")
    n = config.SLOTS_PER_DAY
    # window violations
    for i, s in enumerate(chromosome):
        job = config.JOBS[i]
        if not _is_int(s):
            v += job["duration_h"]
            continue
        if s < job["earliest_start"]:
            v += job["earliest_start"] - s
        end = s + job["duration_h"]
        latest_finish = job["latest_start"] + job["duration_h"]
        if end > latest_finish:
            v += end - latest_finish
    # overlap violations only between chunks of the same appliance
    by_app = {}
    for i, s in enumerate(chromosome):
        job = config.JOBS[i]
        if not _is_int(s):
            continue
        by_app.setdefault(job["appliance"], []).append((s, job["duration_h"]))
    for chunks in by_app.values():
        if len(chunks) < 2:
            continue
        coverage = [0] * n
        for s, dur in chunks:
            for d in range(dur):
                h = s + d
                if 0 <= h < n:
                    coverage[h] += 1
        for h in range(n):
            if coverage[h] > 1:
                v += coverage[h] - 1
    return v


def evaluate(
    chromosome, prices=None, scenario=None, use_solar=None, use_base_load=None
):
    global _EVAL_COUNT
    if len(chromosome) != config.N_GENES:
        raise ValueError(f"chromosome length {len(chromosome)} != {config.N_GENES}")
    if prices is None:
        if scenario is not None:
            if scenario not in config.PRICE_SCENARIOS:
                raise ValueError(f"unknown price scenario: {scenario}`")
            prices = config.PRICE_SCENARIOS[scenario]
        else:
            prices = config.PRICES
    prices = list(prices)
    if len(prices) != config.SLOTS_PER_DAY:
        raise ValueError(f"prices length must be {config.SLOTS_PER_DAY}")
    if any(
        (not isinstance(p, (int, float))) or isinstance(p, bool) or p < 0
        for p in prices
    ):
        raise ValueError("prices must be non-negative numbers")

    if use_solar is None:
        use_solar = config.USE_SOLAR
    if use_base_load is None:
        use_base_load = config.USE_BASE_LOAD

    n = config.SLOTS_PER_DAY
    load = _load_profile(chromosome)
    base = list(config.BASE_LOAD_KW) if use_base_load else [0.0] * n
    solar = list(config.SOLAR_KW) if use_solar else [0.0] * n
    net = [max(0.0, load[h] + base[h] - solar[h]) for h in range(n)]

    v = _violations(chromosome)
    # household cap violations
    cap = getattr(config, "HOUSEHOLD_LIMIT_KW", None)
    if cap is not None:
        for h in range(n):
            if net[h] > cap + 1e-9:
                v += 1

    cost = sum(net[h] * prices[h] for h in range(n))
    peak = max(net) if n else 0.0
    penalty = config.W_PENALTY * v
    objective = config.W_COST * cost + config.W_PEAK * peak + penalty
    feasible = v == 0

    _EVAL_COUNT += 1

    return {
        "feasible": feasible,
        "violations": v,
        "cost": cost,
        "peak": peak,
        "penalty": penalty,
        "objective": objective,
        "components": {
            "cost": cost,
            "peak": peak,
            "violations": v,
            "penalty": penalty,
        },
        "net_import": net,
        "load_profile": load,
    }


def load_profile(chromosome):
    return _load_profile(chromosome)


def net_profile(chromosome, scenario=None, use_solar=None, use_base_load=None):
    res = evaluate(
        chromosome, scenario=scenario, use_solar=use_solar, use_base_load=use_base_load
    )
    # evaluate counts; for profile-only callers this is acceptable
    return res["net_import"]


def baseline_net_profile(scenario=None, use_solar=None, use_base_load=None):
    return net_profile(
        baseline_chromosome(),
        scenario=scenario,
        use_solar=use_solar,
        use_base_load=use_base_load,
    )


def savings(chromosome, scenario=None, use_solar=None, use_base_load=None):
    base_res = evaluate(
        baseline_chromosome(),
        scenario=scenario,
        use_solar=use_solar,
        use_base_load=use_base_load,
    )
    opt_res = evaluate(
        chromosome, scenario=scenario, use_solar=use_solar, use_base_load=use_base_load
    )
    base_cost = base_res["cost"]
    opt_cost = opt_res["cost"]
    base_peak = base_res["peak"]
    opt_peak = opt_res["peak"]
    return {
        "baseline_cost": base_cost,
        "optimized_cost": opt_cost,
        "cost_savings": base_cost - opt_cost,
        "cost_savings_pct": (base_cost - opt_cost) / base_cost * 100.0
        if base_cost
        else 0.0,
        "baseline_peak": base_peak,
        "optimized_peak": opt_peak,
        "peak_savings_pct": (base_peak - opt_peak) / base_peak * 100.0
        if base_peak
        else 0.0,
    }


def before_after_profiles(
    chromosome, scenario=None, use_solar=None, use_base_load=None
):
    return {
        "baseline": baseline_net_profile(
            scenario=scenario, use_solar=use_solar, use_base_load=use_base_load
        ),
        "optimized": net_profile(
            chromosome,
            scenario=scenario,
            use_solar=use_solar,
            use_base_load=use_base_load,
        ),
    }
