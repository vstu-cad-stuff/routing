#!/bin/env python
from data_loader import Clusters
from greedy_algorythm import greedy_init

if __name__ == '__main__':
    data = Clusters()
    matrix = data.generate_matrix('./data/100_p.js', './data/ways.js')
    cluster = data.load_clusters('./data/100_c.js')
    lst = greedy_init(matrix)
    print('cluster_list = {}'.format(lst))
