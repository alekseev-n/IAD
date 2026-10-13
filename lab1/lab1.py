"""Individuals and tournament populations for the assignment problem."""
import math
import random

try:
    from .GA_abstract import Vector, Population
    from .validation import validate_assignment_matrix
except ImportError:  # allow python lab1/lab1_test.py
    from GA_abstract import Vector, Population
    from validation import validate_assignment_matrix


class Employee(Vector):
    """One assignment: index = place, value = employee index."""
    def __init__(self, vector, length, matrix, rng=None):
        self.vector = list(vector)
        self.length = length
        self.matrix = matrix
        self.rng = rng if rng is not None else random
        self.fit = self.fitness(self.vector)

    def cost(self):
        return sum(self.matrix[i][self.vector[i]] for i in range(self.length))

    def fitness(self, vector):
        return 1 / self.cost()

    def mutate(self):
        """Left rotation by 1..n-1; intentionally NOT interval inversion."""
        if self.length < 2:
            return Employee(self.vector, self.length, self.matrix, self.rng)
        i = self.rng.randrange(1, self.length)
        return Employee(self.vector[i:] + self.vector[:i], self.length, self.matrix, self.rng)


class Employees(Population):
    def __init__(self, n, mutation_probability, matrix, t=2, rng=None):
        validate_assignment_matrix(matrix)
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise ValueError("population size must be positive")
        if not isinstance(t, int) or isinstance(t, bool) or t < 1:
            raise ValueError("tournament size must be positive")
        if not 0 <= mutation_probability <= 1:
            raise ValueError("mutation probability must be in [0, 1]")
        self.matrix = matrix
        self.t = t
        self.rng = rng if rng is not None else random
        self.evaluations = 0
        self.best_ever = None
        self.best_ever_cost = math.inf
        super().__init__(n, mutation_probability)
        self.update_best_archive()

    def form_first_population(self):
        n = len(self.matrix)
        self.population = [Employee(self.rng.sample(range(n), k=n), n, self.matrix, self.rng)
                           for _ in range(self.n)]
        self.evaluations += self.n

    def update_best_archive(self):
        if not self.population:
            raise ValueError("population cannot be empty")
        best = max(self.population, key=lambda v: v.fit)
        cost = best.cost()
        if cost < self.best_ever_cost:
            self.best_ever_cost = cost
            self.best_ever = tuple(best.vector)
        return self.best_ever, self.best_ever_cost

    def select(self):
        self.update_best_archive()
        next_population = []
        for _ in range(self.n):
            opponents = [self.rng.choice(self.population) for _ in range(self.t)]
            next_population.append(max(opponents, key=lambda v: v.fit))
        self.population = next_population
        self.update_best_archive()

    def mutate(self):
        mutants = []
        for individual in self.population:
            if self.rng.random() < self.mutation_probability:
                mutants.append(individual.mutate())
        self.evaluations += len(mutants)
        self.population.extend(mutants)
        self.update_best_archive()

    def crossover(self):
        """No crossover in the approved algorithm."""
        return None

    def fitness(self):
        self.fit = sum(v.fit for v in self.population) / len(self.population)
        return self.fit

    def get_best(self):
        best = max(self.population, key=lambda v: v.fit)
        return list(best.vector), best.cost()

    def get_top(self, k):
        if not 0 < k <= 100:
            raise ValueError("k must be in (0, 100]")
        count = math.ceil(self.n * k / 100)
        return sorted(self.population, key=lambda v: v.fit, reverse=True)[:count]

    def extend_population(self, addition):
        self.population.extend(addition)
        self.update_best_archive()
