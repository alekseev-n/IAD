"""Synchronous ring-migration island GA. No CPU-level parallelism."""
from dataclasses import dataclass
from random import Random
from typing import Tuple

try:
    from .lab1 import Employees
    from .validation import validate_assignment_matrix, validate_ga_parameters
except ImportError:
    from lab1 import Employees
    from validation import validate_assignment_matrix, validate_ga_parameters


@dataclass(frozen=True)
class GAConfig:
    num_islands: int = 3
    population_size: int = 50
    mutation_probability: float = 0.7
    tournament_size: int = 2
    max_iterations: int = 1000
    plateau_limit: int = 3
    migration_interval: int = 10
    migration_percent: float = 10


@dataclass(frozen=True)
class GAResult:
    best_vector: Tuple[int, ...]
    best_cost: float
    completed_generations: int
    migration_count: int
    migration_generations: Tuple[int, ...]
    stop_reason: str
    island_best_costs: Tuple[float, ...]
    fitness_evaluations: int


def migrate_ring(islands, percent):
    """Snapshot ALL sources before writing destinations. Returns transfer counts."""
    if len(islands) <= 1:
        return ()
    snapshots = [ga.get_top(percent) for ga in islands]
    for i, outgoing in enumerate(snapshots):
        islands[(i + 1) % len(islands)].extend_population(outgoing)
    for ga in islands:
        ga.select()
    return tuple(len(part) for part in snapshots)


def run_ga_with_migrations(config: GAConfig, matrix, *, seed=None) -> GAResult:
    validate_assignment_matrix(matrix)
    validate_ga_parameters(
        population_size=config.population_size,
        mutation_probability=config.mutation_probability,
        tournament_size=config.tournament_size,
        max_iterations=config.max_iterations,
        plateau_limit=config.plateau_limit,
        migration_interval=config.migration_interval,
        migration_percent=config.migration_percent,
        num_islands=config.num_islands,
    )
    rng = Random(seed)
    islands = [Employees(config.population_size, config.mutation_probability,
                         matrix, config.tournament_size, rng=rng)
               for _ in range(config.num_islands)]
    previous_bests = [ga.best_ever_cost for ga in islands]
    no_improvement = [0] * config.num_islands
    migrations = []
    stop_reason = "max_iterations"
    completed = 0

    for completed in range(1, config.max_iterations + 1):
        for ga in islands:
            ga.mutate()
            ga.select()
        for i, ga in enumerate(islands):
            if ga.best_ever_cost < previous_bests[i]:
                no_improvement[i] = 0
            else:
                no_improvement[i] += 1
            previous_bests[i] = ga.best_ever_cost

        if config.num_islands > 1 and completed % config.migration_interval == 0:
            migrate_ring(islands, config.migration_percent)
            migrations.append(completed)
            for i, ga in enumerate(islands):
                if ga.best_ever_cost < previous_bests[i]:
                    no_improvement[i] = 0
                    previous_bests[i] = ga.best_ever_cost

        all_stalled = all(x >= config.plateau_limit for x in no_improvement)
        if config.num_islands == 1:
            permitted = True
        else:
            permitted = bool(migrations) and completed - migrations[-1] >= config.plateau_limit
        if all_stalled and permitted:
            stop_reason = "plateau_all_islands"
            break

    winner = min(islands, key=lambda ga: ga.best_ever_cost)
    return GAResult(
        best_vector=winner.best_ever,
        best_cost=winner.best_ever_cost,
        completed_generations=completed,
        migration_count=len(migrations),
        migration_generations=tuple(migrations),
        stop_reason=stop_reason,
        island_best_costs=tuple(ga.best_ever_cost for ga in islands),
        fitness_evaluations=sum(ga.evaluations for ga in islands),
    )
