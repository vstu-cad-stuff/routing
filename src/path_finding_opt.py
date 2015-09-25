#!/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt
from copy import deepcopy

# матрица корреспонденции (симметричная относительно главной диагонали)
Node = [170, 1170, 910, 230, 780, 700, 70, 300, 420, 250]
G = [
    [  0, 403, 446, 244, 257, 343,   2, 455,  68, 355],
    [403,   0, 360, 299, 381, 162, 429, 259, 475, 483],
    [446, 360,   0, 490,  92, 159, 197, 281, 333, 200],
    [244, 299, 490,   0, 320, 496, 453, 283, 183, 100],
    [257, 381,  92, 320,   0, 251, 117, 359, 256, 312],
    [343, 162, 159, 496, 251,   0,  99, 170, 478,  55],
    [  2, 429, 197, 453, 117,  99,   0, 171, 487, 131],
    [455, 259, 281, 283, 359, 170, 171,   0, 367,  92],
    [ 68, 475, 333, 183, 256, 478, 487, 367,   0, 212],
    [355, 483, 200, 100, 312,  55, 131,  92, 212,   0]
]
# копируем для использования другими функциями
W = deepcopy(G)

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

# обычный swap
def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

# функция сортировки списка по координатам
def sort_list(C):
    # преобразуем в одно число
    lst = [x * y for x, y in C]
    # список с номерами нодов
    abc = [x for x in range(0, len(lst))]
    i = len(C)
    # сортируем пузырьком
    while i > 1:
        for j in xrange(i-1):
            if lst[j] > lst[j+1]:
                swap(lst, j, j+1)
                swap(abc, j, j+1)
        i -= 1
    return abc

if __name__ == '__main__':
    # загружаем данные из файла
    f = open('./data/points.txt', 'r')
    s = f.read().splitlines()
    f.close()
    # преобразуем данные из файла к виду [[0, 1], ...]
    N = list(map(lambda x: [float(x.split(' ')[0]), float(x.split(' ')[1])], s))
    matrix_width = len(G[0])
    # длина маршрута
    length_of_routes = matrix_width - 1
    # количество маршрутов -- половина от размера массива
    number_of_routes = matrix_width // 2
    write_str = 'path = [\n'
    # делаем number_of_routes маршрутов
    for x in range(number_of_routes):
        path = []
        # находим выходную ноду
        n, m = find_max(G)
        # находим путь из неё
        n, m = max_in_matrix(n, m, Node)
        # добавляем в список
        path.append(n)
        # отмечаем в массиве ноду и ребро
        Node[n] = G[n][m] = -1
        for i in range(length_of_routes):
            # переходим к следующей наилучшей ноде
            n = max_in_list(n, G, path)
            # добавляем в список
            path.append(n)
        print('[{:03d}] path = {}'.format(x, path))
        write_str += '\t{},\n'.format(path)
    # найдём маршрут методом сортировки
    sort_lst = sort_list(N)
    print("[srt] path = {}".format(sort_lst))
    # добавление маршрута методом сортировки
    write_str += '\t{},\n'.format(sort_lst)
    # запись маршрутов
    write_str = write_str[:-2] + '\n];'
    f = open('routing.js', 'w')
    f.write(write_str)
    f.close()