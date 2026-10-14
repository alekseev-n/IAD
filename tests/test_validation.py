import math
import pytest
from lab1.validation import validate_assignment_matrix, validate_ga_parameters
from lab1.lab1 import Employees
from lab1.island_ga import GAConfig, run_ga_with_migrations

@pytest.mark.parametrize('matrix', [[], [[0]], [[-1]], [[math.nan]], [[math.inf]],
                                    [[1,2]], [[1,2],[3]], [[1,'2'],[3,4]], [[True]]])
def test_invalid_matrices_fail_early(matrix):
    with pytest.raises(ValueError):
        validate_assignment_matrix(matrix)
    with pytest.raises(ValueError):
        Employees(3, .7, matrix)

@pytest.mark.parametrize('matrix', [[[1]], [[1,100],[100,1]]])
def test_positive_matrices(matrix):
    validate_assignment_matrix(matrix)
    assert Employees(2, .7, matrix).get_best()[1] > 0

@pytest.mark.parametrize('kw', [{'num_islands':0},{'population_size':0},{'tournament_size':0},
                                {'migration_interval':0},{'migration_percent':0},
                                {'migration_percent':101},{'mutation_probability':-0.1},
                                {'mutation_probability':1.1},{'max_iterations':0},{'plateau_limit':0}])
def test_invalid_parameters(kw):
    with pytest.raises(ValueError):
        run_ga_with_migrations(GAConfig(**kw), [[1]], seed=1)
