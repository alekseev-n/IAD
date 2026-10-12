def run_ga_with_migraions(
        population_size,
        mutation_probability,
        tournament_size,
        max_iterations,
        plateau_limit,
        migration_interval,
        migration_percent,
        matrix
):
    # 1. Инициализируем список независимых островов-популяций
    islands = [
        Employees(n=population_size, mutation_probability=mutation_probability, matrix=matrix, t=tournament_size)
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

        # Проверяем условие остановки по плато
        if len(fitness_history) >= plateau_limit:
            last_3 = fitness_history[-plateau_limit:]
            if max(last_3) - min(last_3) < 0.04 and iteration > 2:
                print(f"-> Остановка по условию плато на {iteration}-й итерации.")
                break

        iteration += 1
    else:
        print(f"-> Достигнут лимит в {max_iterations} итераций.")

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