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
        self.matrix = matrix
        self.fit = self.fitness(vector) # Поменял местами последние 2 строчки, так как фитнесс использует матрицу

    def mutate(self):
        i = random.randrange(1, self.length)
        return Employee(self.vector[i:] + self.vector[:i], self.length, self.matrix)

    def fitness(self, vector): # pyright: ignore[reportIncompatibleMethodOverride]
        return 1 / sum(self.matrix[i][self.vector[i]] for i in range(self.length))


    

class Employees(Population):

    """Класс для решения задачи о расстановке сотрудников с помощью ГА
    @params: population_size \n
    n - размер популяции \n
    mutation_probability - вероятность мутации для каждого вектора. Должна быть высокой. \n
    matrix - матрица стоимостей наёма i-го сотрудника на j-е место \n
    t - количество участников одного раунда турнирного отбора"""

    def __init__(self, n, mutation_probability, matrix, t=2):
        self.matrix = matrix
        super().__init__(n, mutation_probability)
        # self.matrix = matrix Поменял местами, так как суперкласс вызывает form_first_population, который вызывает self.matrix
        self.t = t
        

    def form_first_population(self):
        self.population = []
        chromosome_len = len(self.matrix)
        numbers = range(chromosome_len)
        while len(self.population) < self.n:
            #self.population.append(random.sample(numbers, k=self.n))
            # Список чисел нужно преобразовать к классу employee

            random_vector = random.sample(numbers, k=chromosome_len)
            new_employee = Employee(random_vector, chromosome_len, self.matrix)
            self.population.append(new_employee)

    def select(self):
        """@brief: Турнирный отбор\n
        @params: t - количество участников, из которых выбирается 1 лучший"""

        new_population = []
        new_population_length = 0
        while new_population_length < self.n:
            to_choose = [random.choice(self.population) for _ in range(self.t)]
            new = max(to_choose, key=lambda v: v.fit)
            new_population.append(new)
            new_population_length += 1

        self.population = new_population

    def mutate(self):
        """Функция вместо кроссовера"""

        """for vector in self.population:
            num = random.random()
            if num < self.mutation_probability:
                new = vector.mutate()
                self.population.append(new) """
        mutants = []
        for vector in self.population:
            num = random.random()
            if num < self.mutation_probability:
                new = vector.mutate()
                mutants.append(new)  # Добавляем во временный список

        self.population.extend(mutants)

    def crossover(self):
        pass

    def fitness(self):
        """Функция приспособленности популяции. Записывает приспособленность в переменную класса self.fit и возвращает её"""

        self.fit = sum(v.fit for v in self.population) / len(self.population)
        return self.fit

    def get_best(self):
        """Вспомогательный метод для поиска лучшей особи в популяции"""
        best = max(self.population, key=lambda v: v.fit)

        cost = sum(self.matrix[i][best.vector[i]] for i in range(len(self.matrix)))
        return best.vector, cost

