#!/bin/env python
# -*- coding: utf-8 -*-

N = 'abcd'
W = [300, 200, 400, 500]
G = [
    [  0, 200, 100, 100],
    [200,   0, 150, 300],
    [100, 150,   0, 150],
    [100, 300, 150,   0]
]

# функция поиска максимума в списке (в правой части от главной диагонали)
def find_max(A):
    max_a = A[1][0]
    n, m = 1, 0
    for i in range(1, len(A)):
        for j in range(i+1, len(A)):
            if A[j][i] > max_a:
                max_a = A[j][i]
                n, m = i, j
    return n, m

# функция максимума между двумя вершинами
def max_in(n, m, A):
    if A[n] > A[m]:
        return n, m
    else:
        return m, n

# фунция поиска максимума в списке с нумерацией
def max_lst(A):
    max_a = A[0]
    n = 0
    for i in range(len(A)):
        if A[i] > max_a:
            max_a = A[i] 
            n = i
    return n

if __name__ == '__main__':
    # цикл по маршрутам
    for x in range(3):
        # список для хранения вершин
        path = []
        # находим максимальное ребро в G и получаем номера вершин
        n, m = find_max(G)
        # находим максимальную вершину для старта
        s, r = max_in(n, m, W)
        print('[step0] start point \'{}\' [{}]'.format(N[s], s))
        # закрываем путь назад
        G[m][n] = -1
        # добавляем номер вершины в список
        path.append(s)
        # цикл по вершинам
        for p in range(1, len(W)):
            # находим максимальное ребро в G и получаем номера вершин
            s, r = max_in(n, m, W)
            # делаем выборку по столбцу (куда можно пойти из этой вершины)
            lst = list(map(lambda x: x[r], G))
            # находим максимальный элемент в столбце (лучший вариант)
            n = max_lst(lst)
            print('[step{}]  next point \'{}\' [{}]'.format(p, N[r], r))
            # закрываем путь назад
            G[r][n] = -1
            # добавляем номер вершины в список
            path.append(r)
        print('Result path = {}\n'.format(path))