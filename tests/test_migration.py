from random import Random
from lab1.lab1 import Employees, Employee
from lab1.island_ga import GAConfig, migrate_ring, run_ga_with_migrations


def test_ring_migration_transmits_five_from_each_of_three_islands():
    matrix = [[1 if i==j else 100 for j in range(5)] for i in range(5)]
    islands = [Employees(50, 0, matrix, t=1, rng=Random(i)) for i in range(3)]
    calls = []
    for dest, island in enumerate(islands):
        old = island.extend_population
        def spy(items, destination=dest, inner=old):
            calls.append((destination, len(items)))
            return inner(items)
        island.extend_population = spy
    assert migrate_ring(islands, 10) == (5,5,5)
    assert calls == [(1,5),(2,5),(0,5)]
    assert all(len(ga.population) == 50 for ga in islands)


def test_migration_occurs_at_completed_ten_and_twenty():
    config = GAConfig(num_islands=3, mutation_probability=0,
                      max_iterations=21, plateau_limit=99)
    res = run_ga_with_migrations(config, [[1,1],[1,1]], seed=4)
    assert res.migration_generations == (10,20)
    assert res.migration_count == 2
    assert res.completed_generations == 21
