#!/bin/env python
# -*- coding: utf-8 -*-
# Метод имитации отжига на основе статьи http://habrahabr.ru/post/209610/
# TODO: почитать http://habrahabr.ru/post/210942/
import numpy as np
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
coords = []

# функция загрузки координат кластеров
def loadCoords(file):
    f = open(file, 'r')
    s = f.read().splitlines()
    f.close()
    return list(map(lambda x: [float(x.split(' ')[0]), float(x.split(' ')[1])], s))

# функция расчёта расстояния по http://en.wikipedia.org/wiki/Great-circle_distance
def getDinstance(a, b):
    rad = 6372795 # радиус сферы (Земли)
    dlng = abs(coords[a][1] - coords[b][1]) * np.pi / 180.0
    lat1, lat2 = coords[a][0] * np.pi / 180.0, coords[b][0] * np.pi / 180.0
    p1, p2, p3 = np.cos(lat2), np.sin(dlng), np.cos(lat1)
    p4, p5, p6 = np.sin(lat2), np.sin(lat1), np.cos(lat2)
    p7 = np.cos(dlng)
    y = np.sqrt(np.power(p1 * p2, 2) + np.power(p3 * p4 - p5 * p6 * p7, 2))
    x = p5 * p4 + p3 * p6 * p7
    return rad * np.arctan2(y, x)

# функция расчёта процента перевозки людей
def getEnergy(G, list):
    # суммарное расстояние
    distance = 0
    # количество перевезённых
    coast = 0
    for i in range(0, len(list)-1):
        distance += getDinstance(list[i], list[i+1])
        coast += G[list[i+1]][list[i]]
    return coast * 1.0 / distance

# обычный swap
def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

def generateCandidate(lst):
    i = j = 0
    while i - j < 2:
        i = np.random.randint(0, len(lst))
        j = np.random.randint(0, len(lst))
    i, j = min(i, j), max(i, j)
    # разрезаем список на части (0, i) (i, j) (j, end)
    # и инвертируем середину
    return lst[0:i] + list(reversed(lst[i:j])) + lst[j:]

# инкремент списка для человеко-читаемых списков
def toHR(lst):
    return [x + 1 for x in lst]

if __name__ == '__main__':
    # начальная и конечная температуры
    initTemperature, endTemperature = 100, 1E-10
    # загружаем координаты
    coords = loadCoords('./data/points.txt')
    # создаём список обхода
    current = [x for x in range(10)]
    # перемешиваем его
    np.random.shuffle(current)
    currentEnergy = getEnergy(G, current)
    print('before = {} with {}'.format(toHR(current), currentEnergy))
    T = initTemperature
    for i in range(1, 1000):
        # генерируем кандидата
        candidate = generateCandidate(current)
        # находим его целевую функцию
        candidateEnergy = getEnergy(G, candidate)
        if candidateEnergy > currentEnergy:
            # выбираем нашего кандидата
            currentEnergy = candidateEnergy
            current = candidate
        else:
            # иначе разыгрываем решение
            p = np.exp(-(candidateEnergy-currentEnergy)/T)
            if np.random.random() <= p:
                currentEnergy = candidateEnergy
                current = candidate
        # понижаем температуру
        T -= initTemperature * 0.1 / i
        if T <= endTemperature:
            # выходим если температура приблизилась к конечной
            break
    print(' after = {} with {}'.format(toHR(current), currentEnergy))
