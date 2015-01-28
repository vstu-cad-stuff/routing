#!/bin/env python
# -*- coding: utf-8 -*-

W = [170, 1170, 910, 230, 780, 700, 70, 300, 420, 250]
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

if __name__ == '__main__':
    # загружаем данные из файла
    f = open('./data/points.txt', 'r')
    s = f.read().splitlines()
    f.close()
    # преобразуем данные из файла к виду [[0, 1], ...]
    N = list(map(lambda x: [float(x.split(' ')[0]), float(x.split(' ')[1])], s))
    f = open('routing.js', 'w')
    for x in range(len(W)//2):
        path = []
        n, m = find_max(G)
        n, m = max_in_matrix(n, m, W)
        path.append(n)
        W[n] = -1
        G[n][m] = -1
        for i in range(len(W)-1):
            n = max_in_list(n, G, path)
            path.append(n)
        print('[{:03d}] path = {}'.format(x, path))
        f.write('path[{}] = [\n'.format(x))
        for p in path:
            f.write('\t[{:0.06f}, {:0.06f}],\n'.format(N[p][0], N[p][1]))
        f.write('];\n')
