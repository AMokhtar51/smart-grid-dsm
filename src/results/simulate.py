"""Simulation and results stub (results team - implement this file).

Team 2 hands you their best chromosome (list[int], see docs/HANDOFF.md).
Everything numerical is already computed by evaluator - your job is to wrap
and visualise it:

- evaluator.before_after_profiles(chrom, scenario="tou")
    -> {"baseline": [24 net-import kW values], "optimized": [...]}
- evaluator.savings(chrom, scenario="tou")
    -> {"baseline_cost", "optimized_cost", "cost_savings",
        "cost_savings_pct", "baseline_peak", "optimized_peak",
        "peak_savings_pct"}

What to build (matplotlib, already in requirements.txt):
- before_after_profiles / savings_summary: thin wrappers returning exactly
  what evaluator gives, so team 2's runner can call this module without
  touching evaluator internals.
- plot_profiles(chromosome, scenario=None, out=None): one chart, two lines -
  baseline vs optimised net import (kW) over the 24 hourly slots. This is the
  "load profile before/after optimisation" figure; annotate the peak value of
  each line (peak shaving) and save to results/ (default name
  results/profiles_<scenario>.png).
- save_report(chromosome, scenario=None, out=None): a comparative markdown
  report at results/report_<scenario>.md: cost savings and peak-shaving table
  from savings_summary (baseline vs optimised, absolute + %), plus a per-slot
  table of the two profiles. State the scenario and the appliance sources.

Write nothing outside results/ (the dir exists, kept by results/.gitkeep).

Expected interface:
- before_after_profiles(chromosome, scenario=None) -> dict with "baseline"
  and "optimized" per-slot net import lists.
- savings_summary(chromosome, scenario=None) -> dict from evaluator.savings.
- plot_profiles(chromosome, scenario=None, out=None) -> path of saved figure.
- save_report(chromosome, scenario=None, out=None) -> path of saved report.
"""

from src.optimization import evaluator


def before_after_profiles(chromosome, scenario=None):
    return evaluator.before_after_profiles(chromosome, scenario=scenario)


def savings_summary(chromosome, scenario=None):
    return evaluator.savings(chromosome, scenario=scenario)


def plot_profiles(chromosome, scenario=None, out=None):
    raise NotImplementedError("plot_profiles not implemented in Split 1")


def save_report(chromosome, scenario=None, out=None):
    raise NotImplementedError("save_report not implemented in Split 1")
