"""Exact benchmark solver, never called by the GA."""
try:
    from .validation import validate_assignment_matrix
except ImportError:
    from validation import validate_assignment_matrix


def solve_exact(matrix):
    from scipy.optimize import linear_sum_assignment
    validate_assignment_matrix(matrix)
    rows, cols = linear_sum_assignment(matrix)
    vector = [0] * len(matrix)
    for r, c in zip(rows, cols):
        vector[int(r)] = int(c)
    return tuple(vector), sum(matrix[i][vector[i]] for i in range(len(matrix)))
