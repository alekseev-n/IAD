# Формирование популяции, функцию вычисления приспособленности популяции и алгоритм мутации
# В презентации код и его тестирование
# прийти в 16.10

from GA_abstract import Vector, Population
import random
from itertools import combinations

class Employee(Vector):

    def __init__(self, vector, length, matrix):
        self.vector = vector
        self.length = length
        self.fitness = self.fitness(vector) 
        self.matrix = matrix

    def mutate(self):
        i = random.randrange(self.length)
        return Employee(self.vector[i:] + self.vector[:i], self.length, self.matrix)

    def fitness(self, vector): # pyright: ignore[reportIncompatibleMethodOverride]
        return sum(self.matrix[i][self.vector[i]] for i in range(self.length))


    

class Employees(Population):
    def __init__(self, population_size, max_iterations, n, mutation_probability, matrix):
        super.__init__(population_size, max_iterations, n, mutation_probability)
        self.matrix = matrix
        

    def form_first_population(self):
        vectors = set()
        numbers = range(self.n)
        while len(vectors) < self.n:
            vectors.add(random.sample(numbers, k=self.n))
        self.population = list(vectors)
    
    def select(self):
        amount_to_exclude = len(self.population) - self.n
        tournir_employees = self.population[-amount_to_exclude * 2:]
        tournir_pairs = combinations(tournir_employees, 2)

        for i in tournir_pairs:
            to_exclude = max(i, key=lambda x: x.fitness)
            self.population.remove(to_exclude)

    def mutate(self):
        for vector in self.population:
            num = random.random()
            if num < self.mutation_probability:
                new = vector.mutate()
                self.population.append(new)

    def crossover(self):
        pass
