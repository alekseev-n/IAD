"""Exact solver demo (this file no longer contains a copied GA loop)."""
try:
    from .lab1_test import MATRICES
    from .exact_solver import solve_exact
except ImportError:
    from lab1_test import MATRICES
    from exact_solver import solve_exact

if __name__ == '__main__':
    for name, matrix in MATRICES.items():
        vector, cost = solve_exact(matrix)
        print(name, list(vector), cost)
