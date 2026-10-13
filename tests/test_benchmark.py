import csv
from benchmarks.run_experiments import make_matrix, run_experiments


def test_benchmark_writes_machine_readable_comparable_runs(tmp_path):
    rows, summary = run_experiments([4,5], 2, tmp_path, population_size=5)
    assert len(rows) == 12
    assert len(summary) == 6
    assert all(row['optimum_cost'] <= row['ga_cost'] for row in rows)
    assert all(row['fitness_evaluations'] >= row['population_size_per_island'] for row in rows)
    assert (tmp_path/'runs.csv').exists() and (tmp_path/'summary.csv').exists()
    assert (tmp_path/'config.json').exists()
    with (tmp_path/'runs.csv').open(newline='') as f:
        assert len(list(csv.DictReader(f))) == 12


def test_matrix_creation_reproducible():
    assert make_matrix(4, 42) == make_matrix(4, 42)
