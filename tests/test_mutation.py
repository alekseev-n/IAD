from random import Random
from lab1.lab1 import Employee, Employees

class FixedRandom:
    def randrange(self, a, b):
        assert (a,b)==(1,4)
        return 2


def test_cyclic_shift_preserves_permutation_and_source():
    x = Employee([2,3,0,1], 4, [[1]*4 for _ in range(4)], FixedRandom())
    y = x.mutate()
    assert y.vector == [0,1,2,3]
    assert x.vector == [2,3,0,1]
    assert x is not y


def test_n_one_mutation_returns_separate_individual():
    ga = Employees(2, 1, [[3]], rng=Random(8))
    new = ga.population[0].mutate()
    assert new.vector == [0] and new is not ga.population[0]
    ga.mutate(); ga.select()
    assert ga.get_best()[1] == 3


def test_rotation_reachability_is_only_n_rotations():
    v = [2,3,0,1]
    possibilities = {tuple(v[i:]+v[:i]) for i in range(len(v))}
    assert len(possibilities) == 4
    assert (2,0,3,1) not in possibilities
