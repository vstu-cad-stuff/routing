from data_loader import Clusters
import auxiliary as ax
import numpy as np


def mutation(data, route, parts=2):
    """
    mutation function

    input:
        data  -- cluster data class (correspondence matrix, coordinates)
        route -- route list before mutation
        parts -- number of parts (mutation parameter)
    output:
        route -- route list after mutation
    """
    split_route = ax.toChunk(route, parts)
    new_route = []
    for item in split_route:
        if np.random.random() >= 0.5:
            ax.sortByMetric(data.getSphereDistance, item)
        else:
            ax.sortByMetric(data.getPeople, item)
        new_route += item
    return new_route


def crossover(data, route):
    """
    crossover function

    input:
        data   -- cluster data class (correspondence matrix, coordinates)
        route  -- route list before crossover
    output:
        route  -- route list after crossover
    """
    old_route = route[:]
    peoples = list(map(lambda x: int(data.getPeople(x, x)), old_route))
    new_route = []
    ax.funcRemoveAppend(max, peoples, old_route, new_route)
    i = 0
    while len(old_route) > 0:
        distances = list(map(lambda x: data.getSphereDistance(new_route[i], x), old_route))
        ax.funcRemoveAppend(min, distances, old_route, new_route)
        i += 1
    return new_route


def buildRoutes(data, routes, *, write_result=False, dup_count_max=20, delta=1E-10):
    """
    modify input route network with using genetic algorithm

    input:
        data          -- cluster data class (correspondence matrix, coordinates)
        routes        -- route network
        write_result  -- write result to file
        dub_count_max -- max iteration with identical rate value 
    output:
        new route network
    """
    inf_loop = True
    dup_count = 0
    iteration = 0
    data_set = []
    while inf_loop:
        iteration += 1
        rate_before = ax.routeRating(data, routes)
        print('#{:04} with rate parameter {:.8e}'.format(iteration, rate_before), end='')
        new_routes = []
        for index in range(len(routes)):
            if np.random.random() >= 0.5:
                result = mutation(data, routes[index])
            else:
                result = crossover(data, routes[index])
            new_routes.append(result)
        rate_after = ax.routeRating(data, new_routes)
        print(' delta = {:+.4e}'.format(rate_before - rate_after))
        if rate_after < rate_before:
            routes = new_routes
            dup_count = 0
        elif rate_after - rate_before > delta:
            dup_count += 1
            if dup_count >= dup_count_max:
                inf_loop = False
    if write_result:
        from datetime import datetime
        with open('network-iteration-{:%Y-%m-%d-%H-%M-%S}.js'.format(datetime.now()), 'w') as f:
            f.write('network_list.push({});'.format(routes))
    return routes

if __name__ == '__main__':
    data = Clusters()
    data.generateMatrix('./data/100_p.js', './data/ways.js')
    data.loadClusters('./data/100_c.js')
    init_route = [
        [88, 52, 74, 33, 45, 41, 34, 10, 16, 19, 1],
        [71, 9, 25, 87, 58, 15, 30, 13, 69, 61, 67],
        [38, 32, 36, 70, 80, 39, 85, 81, 21, 89, 67],
        [4, 98, 46, 14, 65, 90, 68, 22, 79, 56, 93],
        [86, 55, 82, 29, 57, 12, 0, 5, 17, 47, 93],
        [96, 26, 50, 72, 48, 43, 18, 35, 49, 59, 20],
        [37, 42, 97, 62, 78, 75, 27, 60, 6, 51, 63],
        [94, 28, 91, 83, 3, 77, 44, 23, 66, 8, 24]
    ]
    print('>> before =', init_route)
    result = buildRoutes(data, init_route)
    print('>>  after =', result)