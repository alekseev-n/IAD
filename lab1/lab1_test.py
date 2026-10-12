import math
from lab1 import Employees
from itertools import permutations


matrices = {
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
TOURNAMENT_SIZE = 2
MAX_ITERATIONS = 1000
PLATEAU_LIMIT = 3

MIGRATION_INTERVAL = 10  # Каждые 10 поколений происходит обмен
MIGRATION_PERCENT = 10  # Передаем 10% лучших особей (5 штук при размере 50)

for test_name, matrix in matrices.items():
    print(f"\n{'=' * 10} {test_name} (Мультипопуляционный ГА) {'=' * 10}")

    # 1. Инициализируем список независимых островов-популяций
    islands = [
        Employees(n=POPULATION_SIZE, mutation_probability=MUTATION_PROBABILITY, matrix=matrix, t=TOURNAMENT_SIZE)
        for _ in range(NUM_ISLANDS)
    ]

    iteration = 0
    fitness_history = []

    # === ГЛАВНЫЙ ЦИКЛ ЭВОЛЮЦИИ ===
    while iteration < MAX_ITERATIONS:

        # Шаг А. Независимая эволюция на каждом острове
        for ga in islands:
            ga.mutate()  # Мутация
            ga.select()  # Отбор лучших

        # Шаг Б. Миграция особей между островами (каждые MIGRATION_INTERVAL поколений)
        if iteration > 0 and iteration % MIGRATION_INTERVAL == 0:
            # Собираем мигрантов (лучших особей) со всех островов в памяти
            migrants_from = [ga.get_top(MIGRATION_PERCENT) for ga in islands]

            # Передаем по схеме "Кольцо"
            for i in range(NUM_ISLANDS):
                next_island_idx = (i + 1) % NUM_ISLANDS
                # Остров (i) отдает своих мигрантов острову (next_island_idx)
                islands[next_island_idx].extend_population(migrants_from[i])

            # Сразу после миграции принудительно делаем отбор (select),
            # чтобы ужать расширившиеся популяции обратно до POPULATION_SIZE
            for ga in islands:
                ga.select()

        # Шаг В. Считаем среднюю общую приспособленность по всем островам для проверки плато
        total_islands_fitness = sum(ga.fitness() for ga in islands) / NUM_ISLANDS
        fitness_history.append(total_islands_fitness)

        # Проверяем условие остановки по плато
        if len(fitness_history) >= PLATEAU_LIMIT:
            last_3 = fitness_history[-PLATEAU_LIMIT:]
            if max(last_3) - min(last_3) < 0.04 and iteration > 2:
                print(f"-> Остановка по условию плато на {iteration}-й итерации.")
                break

        iteration += 1
    else:
        print(f"-> Достигнут лимит в {MAX_ITERATIONS} итераций.")

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

    for p in permutations(range(n_size)):
        current_cost = sum(matrix[i][p[i]] for i in range(n_size))
        if current_cost < best_exact_cost:
            best_exact_cost = current_cost
            best_exact_vector = p

    # Печатаем результаты сравнения
    print(f"Результат Генетического Алгоритма (Лучший остров):")
    print(f"  - Распределение задач (индексы): {ga_vector}")
    print(f"  - Итоговая стоимость: {min_ga_cost}")

    print(f"Результат точного метода (Полный перебор):")
    print(f"  - Распределение задач (индексы): {list(best_exact_vector)}")
    print(f"  - Итоговая стоимость: {best_exact_cost}")

    if min_ga_cost == best_exact_cost:
        print("Мультипопуляционный алгоритм нашел точное решение.")
    else:
        print(f"Найдено субоптимальное решение. Разница с идеалом: {min_ga_cost - best_exact_cost}")