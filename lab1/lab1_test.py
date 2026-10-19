import math
from lab1 import Employees
from itertools import permutations
from scipy.optimize import linear_sum_assignment


matrices = {
    "ideal_matrice": [
        [1, 100, 100, 100, 100],
        [100, 1, 100, 100, 100],
        [100, 100, 1, 100, 100],
        [100, 100, 100, 1, 100],
        [100, 100, 100, 100, 1]
    ],
    "mat1": [[10, 19, 8, 15],
               [13, 11, 17, 10],
               [12, 14, 16, 18],
               [19, 8, 11, 14]]
    ,
    "mat2": [[5, 12, 18, 20, 23, 14],
               [10, 9, 6, 12, 15, 11],
               [14, 17, 12, 8, 11, 16],
               [21, 15, 13, 16, 9, 12],
               [12, 10, 14, 18, 22, 7],
               [8, 13, 16, 11, 15, 10]]
    ,
    "mat3": [[17, 3, 14, 8, 1, 19, 5, 12],
             [11, 20, 2, 15, 7, 18, 13, 5],
             [8, 16, 4, 11, 1, 14, 19, 2],
             [7, 13, 6, 17, 38, 12, 15, 9],
             [20, 4, 10, 51, 14, 6, 18, 3],
             [11, 16, 71, 2, 13, 5, 8, 12],
             [4, 20, 17, 7, 10, 15, 1, 14],
             [6, 12, 4, 64, 53, 3, 34, 43]]
}

NUM_evolution = 3  # Количество независимых популяций (островов)
POPULATION_SIZE = 50  # Размер каждой популяции
MUTATION_PROBABILITY = 0.7
TOURNAMENT_SIZE = 2
MAX_ITERATIONS = 1000
PLATEAU_LIMIT = 3
PLATEAU_DIFF = 2e-4

MIGRATION_INTERVAL = 10  # Каждые 10 поколений происходит обмен
MIGRATION_PERCENT = 10  # Передаем 10% лучших особей (5 штук при размере 50)

def run_ga(
        population_size,
        mutation_probability,
        tournament_size,
        max_iterations,
        plateau_limit,
        plateau_diff,
        matrix
):
    """Функция ГА с миграциями.\n
**Параметры**:
population_size - размер популяции \n
mutation_probability - вероятность мутации \n
tournament_size - количество участников турнира\n
max_iterations - максимальное количество итераций\n
plateau_limit - длина участка, при достижении постоянства на котором, мы останавливаем алгоритм\n
plateau_diff - максимальное колебание целевой функции, при которой участок считается постоянным\n
matrix - матрица, для которой требуется найти решение\n\n

**Возвращает**: кортеж (found_best, iteration, distance)\n
found_best - boolean - нашел ли алгоритм оптимальное решение\n
iteration - integer - сколько итераций потребовалось для нахождения решения \n
distance - integer - разность между нашим и оптимальным значением."""
    
    # 1. Инициализируем список независимых островов-популяций
    evolution = Employees(n=population_size, mutation_probability=mutation_probability, matrix=matrix, t=tournament_size)

    iteration = 1
    fitness_history = []
    fitness_delta = []

    # === ГЛАВНЫЙ ЦИКЛ ЭВОЛЮЦИИ ===
    while iteration < max_iterations:

        # Независимая эволюция на каждом острове

        evolution.mutate()  # Мутация
        evolution.select()  # Отбор лучших


        # Считаем среднюю приспособленность
        current_pop_fitness = evolution.fitness()  # Считаем среднюю приспособленность популяции
        fitness_history.append(current_pop_fitness)
        if len(fitness_history) > 1: fitness_delta.append(abs(fitness_history[-1] - fitness_history[-2]))

        # Проверяем условие остановки по плато. 
        # Теперь проверяем по модулю разности между соседними значениями fitness
        # plateau_limit - считаем, что это минимальное количество разниц между соседними значениями
        # т.е. в истории должно быть не меньше plateau_limit + 1 значений
        if len(fitness_delta) >= plateau_limit:
            diffs = fitness_delta[- plateau_limit:]
            if max(diffs) < plateau_diff:
                print(f"-> Остановка по условию плато на {iteration}-й итерации.")
                break

        iteration += 1
    else:
        print(f"-> Достигнут лимит в {max_iterations} итераций.")

    # 2. Ищем наилучшее решение
    best_vector, best_cost = evolution.get_best()

    # === НАХОЖДЕНИЕ ЭТАЛОНА ===
    n_size = len(matrix)
    best_exact_cost = float('inf')
    best_exact_vector = None

    _, best_exact_vector = linear_sum_assignment(matrix)
    best_exact_vector = [int(i) for i in best_exact_vector]
    best_exact_cost = sum(matrix[i][best_exact_vector[i]] for i in range(len(matrix)))
    
    # Печатаем результаты сравнения
    print(f"Результат Генетического Алгоритма (Лучший остров):")
    print(f"  - Распределение задач (индексы): {best_vector}")
    print(f"  - Итоговая стоимость: {best_cost}")

    print(f"Результат точного метода (Полный перебор):")
    print(f"  - Распределение задач (индексы): {list(best_exact_vector)}")
    print(f"  - Итоговая стоимость: {best_exact_cost}")

    if best_cost == best_exact_cost:
        print("Мультипопуляционный алгоритм нашел точное решение.")
        return (True, iteration, 0)
    else:
        print(f"Найдено субоптимальное решение. Разница с идеалом: {best_cost - best_exact_cost}")
        return (False, iteration, best_cost - best_exact_cost)


if __name__ == "__main__":
    for test_name, matrix in matrices.items():
        print(f"\n{'=' * 10} {test_name} (Мультипопуляционный ГА) {'=' * 10}")
        run_ga(POPULATION_SIZE,
                              MUTATION_PROBABILITY,
                              TOURNAMENT_SIZE,
                              MAX_ITERATIONS,
                              PLATEAU_LIMIT,
                              PLATEAU_DIFF,
                              matrix)

    # count = 0
    # iterations = 0
    # for i in range(100):
    #     result = run_ga_with_migraions(POPULATION_SIZE,
    #                                 MUTATION_PROBABILITY,
    #                                 TOURNAMENT_SIZE,
    #                                 MAX_ITERATIONS,
    #                                 PLATEAU_LIMIT,
    #                                 PLATEAU_DIFF,
    #                                 MIGRATION_INTERVAL,
    #                                 MIGRATION_PERCENT,
    #                                 NUM_evolution,
    #                                 matrices["ideal_matrice"])
    #     count += int(result[0])
    #     iterations += result[1]

    # print(f'На "идеальных" данных алгоритм отработал правильно в {count}% случаев.\n',
    #       f'В среднем это заняло {iterations // 100} итераций')
        