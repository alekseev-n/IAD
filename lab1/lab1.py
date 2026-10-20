# Формирование популяции, функцию вычисления приспособленности популяции и алгоритм мутации
# В презентации код и его тестирование
# прийти в 16.10

import math
import copy
from GA_abstract import Vector, Population
import random
import math
from itertools import combinations

class Employee( Vector ):

    def __init__(self, vector, length, matrix, mutation_percent):
        self.vector = copy.deepcopy(vector)
        self.length = length
        self.matrix = matrix
        self.fit = self.fitness(vector) # Поменял местами последние 2 строчки, так как фитнесс использует матрицу
        self.mutation_percent = mutation_percent

    def mutate(self):
        """Функция мутации. Вырезает кусок из вектора, переворачивает его и вставляет обратно."""
        result = copy.deepcopy(self.vector)
        replace = []
        start = random.randint(1, self.length)
        addition = 1 if self.length == 1 else 2
        stop = start + int(self.length * random.randrange(0, self.mutation_percent) / 100)
        stop = stop if stop - start > 1 else start + addition
        for i in range(start, stop + 1):
            replace.append(self.vector[i % self.length])

        for i in range(start, stop + 1):
            result[i % self.length] = replace[stop - i]

        return Employee(result, self.length, self.matrix, self.mutation_percent)

    def fitness(self, vector): # pyright: ignore[reportIncompatibleMethodOverride]
        f = 1 / sum(self.matrix[i][self.vector[i]] for i in range(self.length))
        self.fit = f
        return f


    

class Employees( Population ):

    """Класс для решения задачи о расстановке сотрудников с помощью ГА
    @params: population_size \n
    n - размер популяции \n
    mutation_probability - вероятность мутации для каждого вектора. Должна быть высокой. \n
    matrix - матрица стоимостей наёма i-го сотрудника на j-е место \n
    t - количество участников одного раунда турнирного отбора\n
    mutation_percent - процент от длины вектора, который переворачивается\n
    elitist_percent - процент особей, который сохраняется"""

    def __init__(self, n, mutation_probability, matrix, mutation_percent, elitist_percent, t=2):
        self.matrix = matrix
        self.population = []
        self.n = n
        self.mutation_probability = mutation_probability
        self.form_first_population(mutation_percent)
        self.elitist_percent = elitist_percent
        # self.matrix = matrix Поменял местами, так как суперкласс вызывает form_first_population, который вызывает self.matrix
        self.t = t
        self.mutation_percent = mutation_percent
        

    def form_first_population(self, mutation_percent):
        self.population = []
        chromosome_len = len(self.matrix)
        numbers = range(chromosome_len)
        while len(self.population) < self.n:
            #self.population.append(random.sample(numbers, k=self.n))
            # Список чисел нужно преобразовать к классу employee

            random_vector = random.sample(numbers, k=chromosome_len)
            new_employee = Employee(random_vector, chromosome_len, self.matrix, mutation_percent)
            self.population.append(new_employee)

    def select(self):
        """@brief: Турнирный отбор\n
        @params: t - количество участников, из которых выбирается 1 лучший"""

        # new_population = sorted(self.population, key=lambda v: v.fit, reverse=True)[:int(self.n * self.elitist_percent)]
        # new_population_length = int(self.n * self.elitist_percent)
        # while new_population_length < self.n:
        #     to_choose = [random.choice(self.population) for _ in range(self.t)]
        #     new = max(to_choose, key=lambda v: v.fit)
        #     new_population.append(Employee(copy.deepcopy(new.vector), len(self.matrix), self.matrix, self.mutation_percent))
        #     new_population_length += 1


        new_population = sorted(self.population, key=lambda v: v.fit, reverse=True)[:int(self.n * self.elitist_percent)]
        new_population_length = int(self.n * self.elitist_percent)
        

        self.fitness()
        self.population = sorted(self.population, key=lambda v: v.fit, reverse=True)
        weights = []
        for i in self.population:
            weights.append(i.fit / self.fit)

        # print(weights)

        count = 0
        while new_population_length < self.n and count < len(weights):
            for _ in range(int(weights[count])):
                new_population.append(Employee(copy.deepcopy(self.population[count].vector),
                                                len(self.matrix), self.matrix, self.mutation_percent))
                new_population_length += 1

            probability = weights[count] - int(weights[count])
            if random.random() < probability:
                new_population.append(Employee(copy.deepcopy(self.population[count].vector),
                                                                len(self.matrix), self.matrix, self.mutation_percent))
                new_population_length += 1
            count += 1
        
        self.population = new_population


    def mutate(self):
        """Функция вместо кроссовера"""

        # mutants = 
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

    def get_top(self, k) -> list[Employee]:
        """
        BRIEF: функция, отбирающая k% лучших особей
        PARAMS:\n
        k - процент лучших особей от популяции, число от 1 до 100\n
        RETURNS: list[Employee] - список лучших объектов
        """

        top_number = math.ceil(self.n * k / 100)
        return sorted(self.population, key=lambda v: v.fit, reverse=True)[:top_number]
        #добавил реверс и ограничение до топ намбер

    def extend_population(self, addition: list[Employee]) -> None:
        """BRIEF: функция, расширяющая популяцию выбранными векторами
        \nPARAMS: addition: list[Employee] - список с добавляемыми векторами"""
        self.population.extend(addition)
