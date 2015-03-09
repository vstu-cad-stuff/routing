#!/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

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

# метод имитации отжига на основе статьи http://habrahabr.ru/post/209610/
def annealing(routes=10, genMax = 1000, matrix=G, initTemperature = 100, endTemperature = 1E-10):
    # создаём список обхода
    current = [x for x in range(routes)]
    # перемешиваем его
    np.random.shuffle(current)
    currentEnergy = getEnergy(G, current)
    print('before = {} with {}'.format(toHR(current), currentEnergy))
    T = initTemperature
    for i in range(1, genMax):
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
            p1 = np.exp(-np.abs(candidateEnergy-currentEnergy)/T)
            p2 = np.random.random()
            if p2 <= p1:
                currentEnergy = candidateEnergy
                current = candidate
        # понижаем температуру
        T = initTemperature * 0.1 / i
        if T <= endTemperature:
            # выходим если температура приблизилась к конечной
            break
    # преобразуем список кластеров к Human Readable формату
    current = toHR(current)
    print(' after = {} with {}'.format(current, currentEnergy))
    return current

if __name__ == '__main__':
    # загружаем координаты кластеров
    coords = loadCoords('./data/points.txt')
    print(' > simulated annealing')
    print('----------------------------------------------------------------')
    annealing(10, 1000, G, 100, 1E-20)
    print('----------------------------------------------------------------')
