#!/bin/env python
# -*- coding: utf-8 -*-
from numpy.random import shuffle
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

# функция расчёта процента перевозки людей
def analyze(G, list):
    # всего людей в нодах
    totalCoast = 0
    # количество перевезённых
    coast = 0
    for x in range(len(G[0])):
        totalCoast += G[x][x]
    for i in range(0, len(list)-1):
        coast += G[list[i+1]][list[i]]
    return coast * 1.0 / totalCoast

# обычный swap
def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

def sort_by_coast(lst):
    coast = []
    for block in lst:
        coast.append(analyze(G, block))
    i = len(lst)
    while i > 1:
        for j in iter(range(i-1)):
            if coast[j] < coast[j+1]:
                swap(coast, j, j+1)
                swap(lst, j, j+1)
        i -= 1

if __name__ == '__main__':
    # создаём несколько случайных списков
    lst = [[x for x in range(10)] for x in range(10)]
    for block in lst:
        # перемещаем список
        shuffle(block)
        # и выведем вместе с их процентами
        print('[gen] {} with {:.4f}'.format(block, analyze(G, block)))
    # сортируем список кандидатов по стоимости
    sort_by_coast(lst)
    print("----")
    # выбираем самое лучшее
    best = lst[0]
    print('[bst] {} with {:.4f}'.format(best, analyze(G, best)))
    # простой эволюционный алгоритм перестановки (мутации) нодов
    for k in range(1, len(best)-1):
        for i in range(len(best)-k):
            gen = deepcopy(best)
            swap(gen, i, i+k)
            b1 = analyze(G, best)
            b2 = analyze(G, gen)
            if b2 > b1:
                best = deepcopy(gen)
    print("----")    
    print('[res] {} with {:.4f}'.format(best, analyze(G, best)))