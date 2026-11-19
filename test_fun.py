from src.constraints import load_appliances, load_pricing
from src.optimization.config import JOBS
from src.optimization.evaluator import (
    baseline_chromosome,
    baseline_net_profile,
    load_profile,
)

chromosome = baseline_chromosome()
app = load_appliances()
price = load_pricing().price_vector()

for i, job in enumerate(JOBS):
    print(f"{job['id']}: start={chromosome[i]}")
