from src.constraints import SLOTS_PER_DAY, load_appliances, load_pricing
from src.optimization import evaluator
from src.optimization.config import JOBS
from src.optimization.evaluator import (
    baseline_chromosome,
    baseline_net_profile,
    load_profile,
)

chromosome = baseline_chromosome()
appliances = load_appliances()
pricing = load_pricing()
price = pricing.price_at(0)

print("Baseline chromosome:", chromosome)
print("—" * 50)
for k, v in evaluator.evaluate(chromosome).items():
    print(f"{k}: {v}")
print("—" * 50)
for i, job in enumerate(JOBS):
    print(f"{job['id']}: start={chromosome[i]}")
