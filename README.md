# Smart Grid Energy Demand Side Management

## Overview
This project focuses on the development of a Smart Grid Energy Demand Side Management system. The system aims to optimize energy consumption by scheduling the operation times of shiftable home appliances over a 24-hour period to minimise electricity costs (based on dynamic time-of-use pricing) andreduce peak load on the power grid, all while respecting user-defined operational time windows.

## What each file does
- `config.py`: appliances, prices, solar, base load, and the algorithm parameters.
- `model.py`: load profile, cost, peak, violation, and fitness. It also holds the evaluation counter.
- `genetic.py`: GA only. It imports model and config.
- `memetic.py`: local search plus the MA. It reuses the GA’s operators.
- `plots.py`: before/after charts and the comparison table.
- `gui.py`: only the interface. It calls the other modules and holds no logic.
- `main.py`: runs baseline, GA, and MA with the same seeds and saves outputs to results/.
- `results/`: figures, tables, and raw run data.