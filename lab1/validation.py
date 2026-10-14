"""Explicit domain restrictions for the assignment GA."""
import math
from numbers import Integral, Real


def validate_assignment_matrix(matrix):
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise ValueError("matrix must be a nonempty square sequence")
    n = len(matrix)
    for row in matrix:
        if not isinstance(row, (list, tuple)) or len(row) != n:
            raise ValueError("matrix must be square")
        for item in row:
            if isinstance(item, bool) or not isinstance(item, Real) or not math.isfinite(item) or item <= 0:
                raise ValueError("all assignment costs must be finite and strictly positive")


def validate_ga_parameters(*, population_size, mutation_probability, tournament_size,
                           max_iterations, plateau_limit, migration_interval, migration_percent,
                           num_islands):
    for name, value in (("population_size", population_size), ("tournament_size", tournament_size),
                        ("max_iterations", max_iterations), ("plateau_limit", plateau_limit),
                        ("migration_interval", migration_interval), ("num_islands", num_islands)):
        if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    for name, value, min_v, max_v in (("mutation_probability", mutation_probability, 0, 1),
                                     ("migration_percent", migration_percent, 0, 100)):
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        if not min_v <= value <= max_v or (name == "migration_percent" and value == 0):
            raise ValueError(f"{name} out of range")
