from lab1.island_ga import GAConfig, run_ga_with_migrations


def test_all_islands_must_survive_migration_and_3_further_generations():
    r = run_ga_with_migrations(GAConfig(num_islands=3, mutation_probability=0), [[1,1],[1,1]], seed=1)
    assert r.completed_generations == 13
    assert r.migration_generations == (10,)
    assert r.stop_reason == 'plateau_all_islands'


def test_single_island_stops_in_three_generations_without_migration():
    r = run_ga_with_migrations(GAConfig(num_islands=1, mutation_probability=0), [[1]], seed=1)
    assert r.completed_generations == 3
    assert r.migration_count == 0


def test_limit_can_stop_before_migration():
    r = run_ga_with_migrations(GAConfig(max_iterations=6, num_islands=3,
                                       mutation_probability=0), [[1]], seed=1)
    assert r.completed_generations == 6
    assert r.stop_reason == 'max_iterations'
    assert r.migration_count == 0


def test_repeatability():
    cfg = GAConfig(num_islands=3, population_size=10, max_iterations=50)
    mat = [[1,100,100],[100,1,100],[100,100,1]]
    assert run_ga_with_migrations(cfg, mat, seed=22) == run_ga_with_migrations(cfg, mat, seed=22)


def test_one_improving_island_delays_global_plateau(monkeypatch):
    import lab1.island_ga as module

    class FakeIsland:
        created = 0
        def __init__(self, n, mutation_probability, matrix, t, rng):
            self.idx = FakeIsland.created
            FakeIsland.created += 1
            self.best_ever_cost = 10.0
            self.best_ever = (0,)
            self.generations = 0
            self.evaluations = 1
        def mutate(self):
            self.generations += 1
            if self.idx == 0 and self.generations == 11:
                self.best_ever_cost = 9.0
        def select(self):
            pass
        def get_top(self, k):
            return [(0,)]
        def extend_population(self, items):
            pass

    monkeypatch.setattr(module, 'Employees', FakeIsland)
    result = module.run_ga_with_migrations(
        GAConfig(num_islands=3, plateau_limit=3, migration_interval=10), [[1]], seed=3)
    assert result.completed_generations == 14
    assert result.stop_reason == 'plateau_all_islands'


def test_migrant_improvement_is_preserved_in_archive(monkeypatch):
    import lab1.island_ga as module

    class FakeIsland:
        created = 0
        def __init__(self, n, mutation_probability, matrix, t, rng):
            self.idx = FakeIsland.created
            FakeIsland.created += 1
            self.best_ever_cost = 10.0 if self.idx == 0 else 50.0
            self.best_ever = (0,)
            self.evaluations = 1
        def mutate(self):
            pass
        def select(self):
            pass
        def get_top(self, k):
            return [self.best_ever_cost]
        def extend_population(self, items):
            if items[0] < self.best_ever_cost:
                self.best_ever_cost = items[0]

    monkeypatch.setattr(module, 'Employees', FakeIsland)
    result = module.run_ga_with_migrations(
        GAConfig(num_islands=3, plateau_limit=13, migration_interval=10,
                 max_iterations=23), [[1]], seed=2)
    assert result.migration_generations == (10, 20)
    assert result.island_best_costs == (10., 10., 10.)
