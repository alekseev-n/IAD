"""Абстрактные классы для генетического алгоритма"""


class Vector:
    """Абстрактный класс особи-вектора генетического алгоритма.
    @methods: __init__ - инициализация вектора\n
    mutate() - мутация
    cross(vector2) - кроссовер - скрещивание со вторым вектором. Либо изменяется сам вектор, 
    либо возвращается новый (оптимальный вариант)
    fitness() - функция приспособленности"""

    def __init__(self):
        pass

    def mutate(self):
        pass

    def cross(self, vector2):
        pass

    def fitness(self, vector):
        pass


class Population:
    """Абстрактный класс для популяции.
    @functions: form_first_population, crossover, mutate, select"""
    def __init__(self, n, mutation_probability) -> None:
        """Params: population_size, n, mutation_probability\n
        n - размер популяции"""

        self.population = []
        self.n = n
        self.mutation_probability = mutation_probability
        self.form_first_population()

    def form_first_population(self):
        pass

    def select(self):
        pass

    def mutate(self):
        for vector in self.population:
            vector.mutate()

    def crossover(self):
        pass

