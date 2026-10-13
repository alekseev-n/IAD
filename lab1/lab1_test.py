"""Command-line smoke runner for the assignment island GA."""
import argparse
try:
    from .island_ga import GAConfig, run_ga_with_migrations
    from .exact_solver import solve_exact
except ImportError:
    from island_ga import GAConfig, run_ga_with_migrations
    from exact_solver import solve_exact

MATRICES = {
    'ideal_matrice': [[1 if i == j else 100 for j in range(5)] for i in range(5)],
    'mat1': [[10,19,8,15],[13,11,17,10],[12,14,16,18],[19,8,11,14]],
    'mat2': [[5,12,18,20,23,14],[10,9,6,12,15,11],
             [14,17,12,8,11,16],[21,15,13,16,9,12],
             [12,10,14,18,22,7],[8,13,16,11,15,10]],
    'mat3': [[17,3,14,8,1,19,5,12],[11,20,2,15,7,18,13,5],
             [8,16,4,11,1,14,19,2],[7,13,6,17,38,12,15,9],
             [20,4,10,51,14,6,18,3],[11,16,71,2,13,5,8,12],
             [4,20,17,7,10,15,1,14],[6,12,4,64,53,3,34,43]],
}
# Preserve the original import name for older student scripts.
matrices = MATRICES


def run_ga_with_migraions(population_size, mutation_probability, tournament_size,
                           max_iterations, plateau_limit, migration_interval,
                           migration_percent, num_islands, matrix, *, seed=None):
    config = GAConfig(num_islands=num_islands, population_size=population_size,
                      mutation_probability=mutation_probability, tournament_size=tournament_size,
                      max_iterations=max_iterations, plateau_limit=plateau_limit,
                      migration_interval=migration_interval, migration_percent=migration_percent)
    return run_ga_with_migrations(config, matrix, seed=seed)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Assignment problem: ring-migration island GA')
    parser.add_argument('--matrix', choices=MATRICES, default='ideal_matrice')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num-islands', type=int, default=3)
    parser.add_argument('--population-size', type=int, default=50)
    parser.add_argument('--mutation-probability', type=float, default=.7)
    parser.add_argument('--tournament-size', type=int, default=2)
    parser.add_argument('--max-iterations', type=int, default=1000)
    parser.add_argument('--plateau-limit', type=int, default=3)
    parser.add_argument('--migration-interval', type=int, default=10)
    parser.add_argument('--migration-percent', type=float, default=10)
    parser.add_argument('--runs', type=int, default=1)
    args = parser.parse_args(argv)
    if args.runs < 1:
        parser.error('--runs must be positive')
    mat = MATRICES[args.matrix]
    cfg = GAConfig(**{key:getattr(args,key) for key in GAConfig.__dataclass_fields__})
    optimum_vector, optimum_cost = solve_exact(mat)
    hits, successful_iters, all_iters = 0, [], []
    for k in range(args.runs):
        res = run_ga_with_migrations(cfg, mat, seed=args.seed+k)
        ok = res.best_cost == optimum_cost
        hits += int(ok)
        all_iters.append(res.completed_generations)
        if ok:
            successful_iters.append(res.completed_generations)
        if args.runs == 1:
            print(f'GA: vector={list(res.best_vector)}, cost={res.best_cost}, '
                  f'generations={res.completed_generations}, migrations={res.migration_count}, '
                  f'stop={res.stop_reason}')
            print(f'Exact: vector={list(optimum_vector)}, cost={optimum_cost}')
    print(f'Exact success: {hits}/{args.runs} ({hits/args.runs:.1%})')
    print(f'Mean generations (all): {sum(all_iters)/args.runs:.2f}')
    if successful_iters:
        print(f'Mean generations (successful only): {sum(successful_iters)/len(successful_iters):.2f}')
    else:
        print('Mean generations (successful only): n/a — no successful runs')


if __name__ == '__main__':
    main()
