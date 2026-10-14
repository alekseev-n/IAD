from itertools import permutations
from lab1.exact_solver import solve_exact
from lab1.lab1_test import MATRICES


def test_exact_ideal_diagonal():
    vec, cost = solve_exact(MATRICES['ideal_matrice'])
    assert vec == (0,1,2,3,4)
    assert cost == 5


def test_exact_agrees_with_bruteforce():
    for matrix in [MATRICES['mat1'], MATRICES['ideal_matrice'], MATRICES['mat2'], MATRICES['mat3']]:
        n=len(matrix)
        exact=min(sum(matrix[i][p[i]] for i in range(n)) for p in permutations(range(n)))
        assert solve_exact(matrix)[1] == exact
