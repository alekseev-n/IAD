from random import Random
from lab1.lab1 import Employee, Employees


def test_tournament_may_lose_best_but_archive_does_not():
    matrix = [[1,100],[100,1]]
    ga = Employees(2, 0, matrix, t=1, rng=Random(0))
    good = Employee([0,1], 2, matrix)
    bad = Employee([1,0], 2, matrix)
    ga.population = [good, bad]
    ga.update_best_archive()
    ga.population = [bad,bad]  # simulate a stochastic tournament losing the optimum
    assert ga.get_best()[1] == 200
    assert ga.best_ever_cost == 2
    assert ga.best_ever == (0,1)
