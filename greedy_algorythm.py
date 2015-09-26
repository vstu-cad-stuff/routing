from copy import deepcopy


# функция поиска нода с максимальным количество людей
def find_max(A):
    max_a = A[0][0]
    n, m = 0, 0
    # простой перебор по всему массиву
    for i in range(1, len(A)):
        for j in range(i+1, len(A)):
            if A[j][i] > max_a:
                max_a = A[j][i]
                n, m = i, j
    return n, m


# функция сравнения двух нодов
def max_in_matrix(n, m, A):
    if A[n] > A[m]:
        return n, m
    else:
        return m, n


# функция поиска максимума в списке
def max_in_list(n, A, path):
    lst = list(map(lambda x: x[n], A))
    for i in range(len(lst)):
        if i in path:
            lst[i] = 0
    max_a, k = lst[0], 0
    for i in range(len(lst)):
        if lst[i] > max_a and i not in path:
            max_a = lst[i]
            k = i
    return k


def greedy_init(matrix):
    # матрица корреспонденции (симметричная относительно главной диагонали)
    Node = []
    length_of_route = len(matrix)
    for i in range(length_of_route):
        Node.append(matrix[i][i])
    # копируем для использования другими функциями
    W = deepcopy(matrix)
    path = []
    # находим выходную ноду
    n, m = find_max(matrix)
    # находим путь из неё
    n, m = max_in_matrix(n, m, Node)
    # добавляем в список
    path.append(n)
    # отмечаем в массиве ноду и ребро
    Node[n] = W[n][m] = -1
    for i in range(length_of_route):
        # переходим к следующей наилучшей ноде
        n = max_in_list(n, matrix, path)
        # добавляем в список
        path.append(n)
    return path
