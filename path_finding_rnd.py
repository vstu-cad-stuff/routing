#!/bin/env python
# -*- coding: utf-8 -*-
from random import randint
from sys import argv

if __name__ == '__main__':
    if len(argv) != 3:
        print('# Random routing generator')
        print('# python {} ./data/points.txt 3'.format(argv[0]))
        print('usage: {} <point-file> <number-of-routes>'.format(argv[0]))
    else:
        # загружаем данные из файла
        f = open(argv[1], 'r')
        s = f.read().splitlines()
        f.close()
        # преобразуем данные из файла к виду [[0, 1], ...]
        N = list(map(lambda x: [float(x.split(' ')[0]), float(x.split(' ')[1])], s))
        # получаем число маршрутов
        number_of_routes = int(argv[2])
        # открываем js файл для записи
        f = open('routing.js', 'w')
        # цикл по количеству маршрутов
        for x in range(number_of_routes):
            # пустой список для маршрутов
            path = []
            # наполняем список маршрутов пока он не будет равен числу кластеров
            while len(path) != len(N):
                # выбираем случайный кластер
                n = randint(0, len(N)-1)
                if n in path:
                    # уже есть в списке -- повторить
                    continue
                else:
                    # добавляем кластер в список
                    path.append(n)
            print('[{:05}] Result path = {}'.format(x + 1, path))
            f.write('path[{}] = [\n'.format(x))
            # записываем координаты кластеров в JS файл
            for p in path:
                f.write('\t[{:0.06f}, {:0.06f}],\n'.format(N[p][0], N[p][1]))
            f.write('];\n')
        f.close()
        print('JS result write to \'routing.js\'');