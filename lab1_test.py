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

POPULATION_SIZE = 50
MUTATION_PROBABILITY = 0.7  # Высокая, так как кроссовера нет
TOURNAMENT_SIZE = 3

for test_name, matrix in matrices.items():
    print(f"\n{'=' * 10} {test_name} {'=' * 10}")

    # Инициализируем популяцию ГА
    # n — размер популяции (возьмем 50 особей)
    ga = Employees(n=POPULATION_SIZE, mutation_probability=MUTATION_PROBABILITY, matrix=matrix, t=TOURNAMENT_SIZE)

    iteration = 0
    max_iterations = 1000

    # Для отслеживания плато (3 последние итерации)
    fitness_history = []
    plateau_limit = 3

    # === ГЛАВНЫЙ ЦИКЛ ЭВОЛЮЦИИ ===
    while iteration < max_iterations:
        ga.select()  # Отбор лучших
        ga.mutate()  # Мутация

        current_pop_fitness = ga.fitness()  # Считаем среднюю приспособленность популяции
        fitness_history.append(current_pop_fitness)

        # Проверяем условие остановки: если последние 3 значения практически не изменились
        if len(fitness_history) >= plateau_limit:
            last_3 = fitness_history[-plateau_limit:]
            # Если разница между макс и мин за последние 3 шага ничтожна
            if max(last_3) - min(last_3) < 1e-6:
                print(f"-> Остановка по условию плато на {iteration}-й итерации.")
                break

        iteration += 1
    else:
        print(f"-> Достигнут лимит в {max_iterations} итераций.")

    # Получаем лучший результат от ГА
    ga_vector, ga_cost = ga.get_best()

    # === НАХОЖДЕНИЕ ЭТАЛОНА ЧЕРЕЗ ПЕРЕБОР ===
    n_size = len(matrix)
    best_exact_cost = float('inf')
    best_exact_vector = None

    # Находим математически точный минимум, перебирая все перестановки задач
    for p in permutations(range(n_size)):
        current_cost = sum(matrix[i][p[i]] for i in range(n_size))
        if current_cost < best_exact_cost:
            best_exact_cost = current_cost
            best_exact_vector = p

    # Печатаем результаты сравнения
    print(f"Результат Генетического Алгоритма:")
    print(f"  - Распределение задач (индексы): {ga_vector}")
    print(f"  - Итоговая стоимость: {ga_cost}")

    print(f"Результат точного метода (Полный перебор):")
    print(f"  - Распределение задач (индексы): {list(best_exact_vector)}")
    print(f"  - Итоговая стоимость: {best_exact_cost}")

    if ga_cost == best_exact_cost:
        print("Успех!")
    else:
        print(f"ГА нашел хорошее, но локальное решение. Разница с идеалом: {ga_cost - best_exact_cost}")