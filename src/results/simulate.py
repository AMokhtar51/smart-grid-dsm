"""Simulation and results stub (results team).

Expected interface:
- before_after_profiles(chromosome, scenario=None) -> dict with "baseline" and "optimized" per-slot net import lists.
- savings_summary(chromosome, scenario=None) -> dict from evaluator.savings.
- plot_profiles(...) / save_report(...) for charts and tables.
"""


def before_after_profiles(chromosome, scenario=None):
    raise NotImplementedError("Simulation not implemented in Split 1")


def savings_summary(chromosome, scenario=None):
    raise NotImplementedError("Simulation not implemented in Split 1")