import math
from lab1 import Employees
from itertools import permutations
from scipy.optimize import linear_sum_assignment
from termination import plateau_reached


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

NUM_ISLANDS = 3  # Количество независимых популяций (островов)
POPULATION_SIZE = 50  # Размер каждой популяции
MUTATION_PROBABILITY = 0.7
MUTATION_PERCENT = 30 # процент от длины элемента вектора, который переворачивается в ходе мутации
TOURNAMENT_SIZE = 2
MAX_ITERATIONS = 1000
PLATEAU_LIMIT = 3
PLATEAU_DIFF = 2e-4
ELITIST_PERCENT = 0.2

MIGRATION_INTERVAL = 10  # Каждые 10 поколений происходит обмен
MIGRATION_PERCENT = 10  # Передаем 10% лучших особей (5 штук при размере 50)

def run_ga_with_migrations(
        population_size,
        mutation_probability,
        mutation_percent,
        tournament_size,
        max_iterations,
        plateau_limit,
        plateau_diff,
        migration_interval,
        migration_percent,
        num_islands,
        elitist_percent,
        matrix
):
    """Функция ГА с миграциями.\n
**Параметры**:
population_size - размер популяции \n
mutation_probability - вероятность мутации \n
mutation_percent - процент от длины элемента вектора, который переворачивается в ходе мутации\n
tournament_size - количество участников турнира\n
max_iterations - максимальное количество итераций\n
plateau_limit - длина участка, при достижении постоянства на котором, мы останавливаем алгоритм\n
plateau_diff - максимальное колебание целевой функции, при которой участок считается постоянным\n
migration_interval - периодичность миграции\n
migration_percent - процент прибавления размера популяции острова после миграции\n
num_islands - количество островов\n
matrix - матрица, для которой требуется найти решение\n\n
**Возвращает**: кортеж (found_best, iteration, distance)\n
found_best - boolean - нашел ли алгоритм оптимальное решение\n
iteration - integer - сколько итераций потребовалось для нахождения решения \n
distance - integer - разность между нашим и оптимальным значением."""
    
    # 1. Инициализируем список независимых островов-популяций
    islands = [
        Employees(n=population_size, 
                  mutation_probability=mutation_probability, 
                  matrix=matrix, 
                  mutation_percent=mutation_percent, 
                  elitist_percent=elitist_percent,
                  t=tournament_size)
        for _ in range(num_islands)
    ]

    iteration = 0
    fitness_history = []

    # === ГЛАВНЫЙ ЦИКЛ ЭВОЛЮЦИИ ===
    while iteration < max_iterations:

        # Шаг А. Независимая эволюция на каждом острове
        for ga in islands:
            ga.mutate()  # Мутация
            ga.select()  # Отбор лучших
        iteration += 1

        # Шаг Б. Миграция особей между островами (каждые migration_interval поколений)
        if iteration > 0 and iteration % migration_interval == 0:
            # Собираем мигрантов (лучших особей) со всех островов в памяти
            migrants_from = [ga.get_top(migration_percent) for ga in islands]

            # Передаем по схеме "Кольцо"
            for i in range(num_islands):
                next_island_idx = (i + 1) % num_islands
                # Остров (i) отдает своих мигрантов острову (next_island_idx)
                islands[next_island_idx].extend_population(migrants_from[i])

            # Сразу после миграции принудительно делаем отбор (select),
            # чтобы ужать расширившиеся популяции обратно до population_size
            for ga in islands:
                ga.select()

        # Шаг В. Считаем среднюю общую приспособленность по всем островам для проверки плато
        total_islands_fitness = sum(ga.fitness() for ga in islands) / num_islands
        fitness_history.append(total_islands_fitness)
        if plateau_reached(fitness_history, plateau_limit, plateau_diff):
            break

    # else:
        # print(f"-> Достигнут лимит в {max_iterations} итераций.")

    # 2. Ищем наилучшее решение среди абсолютно всех островов
    best_vectors = []
    best_costs = []
    for ga in islands:
        v, c = ga.get_best()
        best_vectors.append(v)
        best_costs.append(c)

    min_ga_cost = min(best_costs)
    best_island_idx = best_costs.index(min_ga_cost)
    ga_vector = best_vectors[best_island_idx]

    # === НАХОЖДЕНИЕ ЭТАЛОНА ЧЕРЕЗ ПЕРЕБОР ===
    n_size = len(matrix)
    best_exact_cost = float('inf')
    best_exact_vector = None

    _, best_exact_vector = linear_sum_assignment(matrix)
    best_exact_vector = [int(i) for i in best_exact_vector]
    best_exact_cost = sum(matrix[i][best_exact_vector[i]] for i in range(len(matrix)))
    
    # Печатаем результаты сравнения
    # print(f"Результат Генетического Алгоритма (Лучший остров):")
    # print(f"  - Распределение задач (индексы): {ga_vector}")
    # print(f"  - Итоговая стоимость: {min_ga_cost}")

    # print(f"Результат точного метода (Полный перебор):")
    # print(f"  - Распределение задач (индексы): {list(best_exact_vector)}")
    # print(f"  - Итоговая стоимость: {best_exact_cost}")

    if min_ga_cost == best_exact_cost:
        # print("Мультипопуляционный алгоритм нашел точное решение.")
        return (True, iteration, 0)
    else:
        # print(f"Найдено субоптимальное решение. Разница с идеалом: {min_ga_cost - best_exact_cost}")
        return (False, iteration, (min_ga_cost - best_exact_cost) / best_exact_cost)


if __name__ == "__main__":
    for test_name, matrix in matrices.items():
        # print(f"\n{'=' * 10} {test_name} (Мультипопуляционный ГА) {'=' * 10}")
        run_ga_with_migrations(POPULATION_SIZE,
                              MUTATION_PROBABILITY,
                              MUTATION_PERCENT,
                              TOURNAMENT_SIZE,
                              MAX_ITERATIONS,
                              PLATEAU_LIMIT,
                              PLATEAU_DIFF,
                              MIGRATION_INTERVAL,
                              MIGRATION_PERCENT,
                              NUM_ISLANDS,
                              ELITIST_PERCENT,
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
    #                                 NUM_ISLANDS,
    #                                 matrices["ideal_matrice"])
    #     count += int(result[0])
    #     iterations += result[1]

    # print(f'На "идеальных" данных алгоритм отработал правильно в {count}% случаев.\n',
    #       f'В среднем это заняло {iterations // 100} итераций')
        