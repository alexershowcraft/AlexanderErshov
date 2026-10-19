import random
import math
import collections
import matplotlib.pyplot as plt

#Часть 1

#Генерация поля
def generate_field(rows=5, cols=5, num_traps=3):

    #Создание клеток
    available_cells = [(r, c) for r in range(rows) for c in range(cols) if (r, c) != (0, 0)]
    
    #Ловушки
    random.shuffle(available_cells)
    
    target = available_cells.pop()
    traps = set(available_cells[:num_traps])
    
    return rows, cols, target, traps

#Построение графа
def build_graph(rows, cols, traps):
    graph = {}
    for r in range(rows):
        for c in range(cols):
            if (r, c) in traps:
                continue # В ловушку мы не переходим
            
            neighbors = []
            # Проверка направления
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                # Проверка выхода за границы поля
                if 0 <= nr < rows and 0 <= nc < cols:
                    if (nr, nc) not in traps: # Если сосед - не ловушка
                        neighbors.append((nr, nc))
            
            graph[(r, c)] = neighbors
    return graph

# Поиск кратчайшего пути
def bfs_shortest_path(graph, start, target):

    if start == target:
        return 0
        
    queue = collections.deque([(start, 0)]) # (текущая_клетка, длина_пути)
    visited = set([start])
    
    while queue:
        current_node, distance = queue.popleft()
        
        for neighbor in graph.get(current_node, []):
            if neighbor == target:
                return distance + 1
                
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
                
    return None # Путь не найден

#Часть 2

def simulate_random_walk(rows, cols, target, traps, start=(0, 0), max_steps=10000):
#Один прогон случайного блуждания.
    current = start
    steps = 0
    visited_cells = [current]
    
    while steps < max_steps:
        if current == target:
            return True, steps, visited_cells
        
        # Если каким-то образом попали в ловушку
        if current in traps:
            return False, steps, visited_cells
            
        # Находим всех соседей, не выходя за границы поля
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = current[0] + dr, current[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbors.append((nr, nc))
                
        # Робот выбирает случайного соседа
        current = random.choice(neighbors)
        visited_cells.append(current)
        steps += 1
        
        # Если он наступил на ловушку - неудача
        if current in traps:
            return False, steps, visited_cells
            
    return False, steps, visited_cells # Превышен лимит шагов

def run_monte_carlo(rows, cols, target, traps, K=100000):
    # Серия экспериментов.
    # Собирает статистику.
    successes = 0
    success_steps = []
    fail_steps = []
    visit_counts = collections.Counter()
    
    for _ in range(K):
        success, steps, visited = simulate_random_walk(rows, cols, target, traps)
        
        visit_counts.update(visited) # Считаем посещения для тепловой карты
        
        if success:
            successes += 1
            success_steps.append(steps)
        else:
            fail_steps.append(steps)
            
    prob_success = successes / K
    avg_success_steps = sum(success_steps) / len(success_steps) if success_steps else 0
    avg_fail_steps = sum(fail_steps) / len(fail_steps) if fail_steps else 0
    most_visited = visit_counts.most_common(1)[0] if visit_counts else (None, 0)
    
    return prob_success, avg_success_steps, avg_fail_steps, most_visited, success_steps, visit_counts

#Часть 3

def print_field(rows, cols, target, traps, start=(0,0)):
    #Вспомогательная функция для текстового вывода поля
    print("\nСгенерированное поле (S - старт, T - цель, X - ловушка, . - пусто):")
    for r in range(rows):
        row_str = ""
        for c in range(cols):
            if (r, c) == start: row_str += " S "
            elif (r, c) == target: row_str += " T "
            elif (r, c) in traps: row_str += " X "
            else: row_str += " . "
        print(row_str)
    print()

def main():
    #часть 1 итог
    print("\nЧАСТЬ 1")
    ROWS, COLS = 5, 5
    NUM_TRAPS = 3
    
    # 1. Генерация поля
    rows, cols, target, traps = generate_field(ROWS, COLS, NUM_TRAPS)
    print_field(rows, cols, target, traps)
    
    # 2. Построение графа
    graph = build_graph(rows, cols, traps)
    
    # 3. Поиск кратчайшего пути
    shortest_path_len = bfs_shortest_path(graph, (0, 0), target)
    print(f"Кратчайший путь (BFS) от старта до цели: {shortest_path_len} шагов.")
    if shortest_path_len is None:
        print("Внимание: Путь до цели заблокирован ловушками")

    #часть 2 итог
    print("\nЧАСТЬ 2")
    print("Запускаем симуляцию 100 000 раз. Пожалуйста, подождите...")
    K = 100000
    prob, avg_s, avg_f, most_vis, success_steps_list, visit_counts = run_monte_carlo(
        rows, cols, target, traps, K
    )
    
    print(f"\nРезультаты статистики (из {K} попыток):")
    print(f"Эмпирическая вероятность успеха: {prob:.4f} ({prob*100:.2f}%)")
    print(f"Мат. ожидание шагов для УСПЕШНЫХ попыток: {avg_s:.2f}")
    print(f"Мат. ожидание шагов для НЕУСПЕШНЫХ попыток: {avg_f:.2f}")
    print(f"Клетка, где робот был чаще всего (мода): {most_vis[0]} (посещений: {most_vis[1]})")

    #часть 3 итог
    print("\nЧАСТЬ 3")

    # 1. Сравнение
    if shortest_path_len and avg_s > 0:
        inefficiency = avg_s / shortest_path_len
        print(f"Сравнение: Кратчайший путь = {shortest_path_len} шагов.")
        print(f"Средний путь при случайном блуждании = {avg_s:.2f} шагов.")
        print(f"Вывод: Случайное блуждание неэффективнее оптимального маршрута в {inefficiency:.2f} раз(а).")
    else:
        print("Сравнение невозможно (цель недостижима или нет успешных попыток).")

    # 2. Визуализация
    if success_steps_list:
        plt.figure(figsize=(10, 6))
        # Ограничим ось X, чтобы график не был слишком широким из-за редких долгих прогулок
        plt.hist(success_steps_list, bins=50, color='skyblue', edgecolor='black', range=(0, max(success_steps_list)*0.5))
        plt.title('Распределение количества шагов для успешных попыток')
        plt.xlabel('Количество шагов')
        plt.ylabel('Частота (количество попыток)')
        plt.grid(axis='y', alpha=0.75)
        print("\n[График] Гистограмма распределения шагов сохранена/открыта.")
        plt.show()
    else:
        print("\nУспешных попыток не было, график не построен.")

print("\nОтчет")
print("В ходе работы было сгенерировано поле 5x5 с 3 ловушками. С помощью алгоритма BFS")
print("был найден детерминированный кратчайший путь. Затем проведено 100 000 симуляций")
print("случайного блуждания (Метод Монте-Карло). Анализ показал, что случайный робот")
print("тратит в среднем в разы больше шагов, чем оптимальный путь, а также имеет риск")
print("попасть в ловушку, что подтверждает неэффективность случайного блуждания.")

if __name__ == "__main__":
    main()