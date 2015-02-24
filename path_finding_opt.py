#!/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt
from copy import deepcopy

G = [
    [170,  403, 446, 244, 257, 343,   2, 455,  68, 355],
    [403, 1170, 360, 299, 381, 162, 429, 259, 475, 483],
    [446,  360, 910, 490,  92, 159, 197, 281, 333, 200],
    [244,  299, 490, 230, 320, 496, 453, 283, 183, 100],
    [257,  381,  92, 320, 780, 251, 117, 359, 256, 312],
    [343,  162, 159, 496, 251, 700,  99, 170, 478,  55],
    [  2,  429, 197, 453, 117,  99,  70, 171, 487, 131],
    [455,  259, 281, 283, 359, 170, 171, 300, 367,  92],
    [ 68,  475, 333, 183, 256, 478, 487, 367, 420, 212],
    [355,  483, 200, 100, 312,  55, 131,  92, 212, 250]
]
W = deepcopy(G)

def find_max(A):
    max_a = A[0][0]
    n, m = 0, 0
    for i in range(1, len(A)):
        for j in range(i+1, len(A)):
            if A[j][i] > max_a:
                max_a = A[j][i]
                n, m = i, j
    return n, m

def max_in_matrix(n, m, A):
    if A[n] > A[m]:
        return n, m
    else:
        return m, n

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

def analyze(G, list):
    totalCoast = 0
    coast = 0
    for x in range(len(G[0])):
        totalCoast += G[x][x]
    for i in range(0, len(list)-1):
        sub = G[list[i+1]][list[i]]
        coast += sub
    return coast * 1.0 / totalCoast

def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

def sort_list(C):
    lst = [x * y for x, y in C]
    abc = [x for x in range(0, len(lst))]
    i = len(C)
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
    write_str = 'path = [\n'
    for x in range(matrix_width//2):
        path = []
        n, m = find_max(G)
        n, m = max_in_matrix(n, m, W)
        path.append(n)
        G[n][n] = G[n][m] = -1
        for i in range(matrix_width-1):
            n = max_in_list(n, G, path)
            path.append(n)
        print('[{:03d}] path = {}, with cost = {:0.04f}'.format(x, path, analyze(W, path)))
        write_str += '\t['
        for p in path:
            write_str += '[{:0.06f}, {:0.06f}],\n\t '.format(N[p][0], N[p][1])
        write_str = write_str[:-3] + '],\n'
    # найдём маршрут методом сортировки
    sort_lst = sort_list(N)
    print("[srt] path = {}, with cost = {:0.04f}".format(sort_lst, analyze(W, sort_lst)))
    # добавление маршрута методом сортировки
    write_str += '\t['
    for p in sort_lst:
        write_str += '[{:0.06f}, {:0.06f}],\n\t '.format(N[p][0], N[p][1])
    write_str = write_str[:-3] + '],\n'
    # запись маршрутов
    write_str = write_str[:-2] + '\n];'
    f = open('routing.js', 'w')
    f.write(write_str)
    f.close()