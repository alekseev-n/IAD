"""Reproducible comparison with identical matrices and seeded GA runs."""
import argparse
import csv
import json
import random
import statistics
import sys
from dataclasses import replace
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab1.exact_solver import solve_exact
from lab1.island_ga import GAConfig, run_ga_with_migrations


def make_matrix(n, seed):
    rng = random.Random(seed)
    return [[rng.randint(1, 100) for _ in range(n)] for _ in range(n)]


def run_experiments(sizes, seeds, output_dir, population_size=50, seed_base=20261014):
    if not sizes or any(n < 1 for n in sizes) or seeds < 1 or population_size < 1:
        raise ValueError('sizes, seeds and population size must be positive')
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    modes = [('single_50', 1, population_size),
             ('islands_3x50', 3, population_size),
             ('single_budget_matched', 1, 3 * population_size)]
    for n in sizes:
        matrix_seed = seed_base + n * 1000
        matrix = make_matrix(n, matrix_seed)
        optimum_vector, optimum = solve_exact(matrix)
        for j in range(seeds):
            rng_seed = seed_base + j
            for name, islands, pop in modes:
                cfg = GAConfig(num_islands=islands, population_size=pop)
                start = perf_counter()
                result = run_ga_with_migrations(cfg, matrix, seed=rng_seed)
                elapsed = perf_counter() - start
                rows.append({
                    'dimension': n, 'matrix_seed': matrix_seed,
                    'seed': rng_seed, 'mode': name, 'num_islands': islands,
                    'population_size_per_island': pop,
                    'optimum_cost': optimum, 'ga_cost': result.best_cost,
                    'success': int(result.best_cost == optimum),
                    'gap_pct': 100 * (result.best_cost-optimum) / optimum,
                    'elapsed_seconds': round(elapsed,6),
                    'generations': result.completed_generations,
                    'migration_count': result.migration_count,
                    'fitness_evaluations': result.fitness_evaluations,
                    'stop_reason': result.stop_reason,
                })
    detail_path = output_dir / 'runs.csv'
    with detail_path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    aggregate=[]
    for n in sizes:
        for name, islands, pop in modes:
            sample=[row for row in rows if row['dimension']==n and row['mode']==name]
            aggregate.append({
                'dimension':n,'mode':name,'runs':len(sample),
                'success_rate':sum(row['success'] for row in sample)/len(sample),
                'mean_gap_pct':statistics.mean(row['gap_pct'] for row in sample),
                'median_gap_pct':statistics.median(row['gap_pct'] for row in sample),
                'stdev_gap_pct':statistics.pstdev(row['gap_pct'] for row in sample),
                'mean_seconds':statistics.mean(row['elapsed_seconds'] for row in sample),
                'mean_generations':statistics.mean(row['generations'] for row in sample),
                'mean_evaluations':statistics.mean(row['fitness_evaluations'] for row in sample),
            })
    summary_path=output_dir / 'summary.csv'
    with summary_path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(aggregate[0]))
        writer.writeheader();writer.writerows(aggregate)
    with (output_dir/'config.json').open('w',encoding='utf-8') as f:
        json.dump({'dimensions':sizes,'runs_per_dimension_and_mode':seeds,
                   'seed_base':seed_base,'population_size':population_size,
                   'modes':modes,'default_ga_config':GAConfig().__dict__}, f,
                  ensure_ascii=False,indent=2)
    return rows, aggregate


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sizes',type=int,nargs='+',default=[4,5,8,16,32,64])
    parser.add_argument('--seeds',type=int,default=30)
    parser.add_argument('--population-size',type=int,default=50)
    parser.add_argument('--seed-base',type=int,default=20261014)
    parser.add_argument('--output-dir',default='benchmarks/results')
    args=parser.parse_args(argv)
    rows, summary=run_experiments(args.sizes,args.seeds,args.output_dir,
                                  args.population_size,args.seed_base)
    print('Completed',len(rows),'runs; summary:')
    for s in summary:
        print(f"n={s['dimension']:>2} {s['mode']:<22} "
              f"hit={s['success_rate']:.1%}, avg gap={s['mean_gap_pct']:.2f}%, "
              f"avg time={s['mean_seconds']:.4f}s, evals={s['mean_evaluations']:.0f}")

if __name__=='__main__':
    main()
