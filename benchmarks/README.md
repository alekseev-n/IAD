# Reproducible experiments

Run from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python benchmarks/run_experiments.py --sizes 4 5 8 16 32 64 --seeds 30 \
  --population-size 50 --seed-base 20261014 --output-dir benchmarks/results
```

Files produced: `runs.csv` (one line per seeded run), `summary.csv` (success rate, mean/median/population-SD relative gap, wall-clock seconds, generations and fitness evaluations), `config.json` (full config and seed base). Matrices are generated with **strictly positive** costs; the same matrix is used for each mode at a given dimension. SciPy is used **only** for an independent exact comparison, never in GA selection/mutation.

Modes: `single_50` (one island × 50), `islands_3x50` (three islands × 50) and `single_budget_matched` (one island × 150). The matched mode roughly aligns starting population/evaluation budgets, but actual `fitness_evaluations` must still be compared because runs can stop after different numbers of generations. With sequential islands, 3-island execution is **not** simultaneous and has no guaranteed runtime benefit. Results are stochastic and depend on both matrix seed and GA seed. Report only measured values from the CSV.

Quick smoke test:

```bash
python benchmarks/run_experiments.py --sizes 4 5 --seeds 2 --output-dir /tmp/iad-smoke
```
