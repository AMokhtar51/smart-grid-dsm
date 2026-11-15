# data/raw/

Raw downloaded datasets live here and are NOT committed to git.

Current source: REFIT Electrical Load Measurements (cleaned), Zenodo record
5063428, CC BY 4.0 - https://zenodo.org/records/5063428

Re-download manually or just run:

    python -m src.data.collect --house 2

(`collect.py` fetches `CLEAN_House2.csv`, ~325 MB, and parses it into
`data/processed/appliances.json`.)
