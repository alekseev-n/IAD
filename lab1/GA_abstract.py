"""Shared interfaces for permutation-based genetic algorithms."""

class Vector:
    def mutate(self) -> "Vector":
        raise NotImplementedError

    def cross(self, vector2):
        raise NotImplementedError

    def fitness(self, vector):
        raise NotImplementedError

class Population:
    def __init__(self, n, mutation_probability):
        self.population = []
        self.n = n
        self.mutation_probability = mutation_probability
        self.form_first_population()

    def form_first_population(self):
        raise NotImplementedError

    def select(self):
        raise NotImplementedError

    def mutate(self):
        raise NotImplementedError

    def crossover(self):
        raise NotImplementedError
