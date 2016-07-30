from data_loader import Clusters
from randomcolor.randomcolor import RandomColor
from polyline.codec import PolylineCodec
import auxiliary as ax
import numpy as np
import json as js
import geojson as gs
import requests

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
            ax.sortByMetric(data.getOSRMDistance, item)
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
        distances = list(map(lambda x: data.getOSRMDistance(new_route[i], x), old_route))
        ax.funcRemoveAppend(min, distances, old_route, new_route)
        i += 1
    return new_route


def buildRoutes(data, routes, *, dup_count_max=10, delta=1E-8):
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
        if rate_after > rate_before:
            routes = new_routes
            dup_count = 0
        elif rate_after - rate_before < delta:
            dup_count += 1
            if dup_count >= dup_count_max:
                inf_loop = False
    return routes

def loadRoadNetwork(data, file):
    id_list = []
    with open(file, 'r') as fp:
        load_data = fp.read().replace('\n', '')
        js_data = js.loads('{"RN":' + load_data[5:-3] + ']}')
        return js_data['RN']
    raise('Unexpected error')

def dump_result(list_data, data, filename):
    def route_geometry(ids):
        viaroute = 'http://127.0.0.1:5000/viaroute?alt=false&geometry=true'
        for item in ids:
            try:
                coords = data.clusters[item]
                viaroute += '&loc={},{}'.format(coords[1], coords[0])
            except:
                print('>> note {} not found!'.format(item))
                sys.exit()
        req = js.loads(requests.get(viaroute).text)
        return list(map(
            lambda x: [x[1] / 10.0, x[0] / 10.0], PolylineCodec().decode(req['route_geometry'])
        ))

    with open(filename, 'w') as jfile:
        rnd_color = RandomColor()
        colors = rnd_color.generate(count=len(list_data))
        features = []
        index = 1
        features.append(gs.MultiPoint(list(data.clusters.values())))
        for item in list_data:
            color = colors.pop()
            terminal = [item[0], item[-1]]
            RP = route_geometry(item)
            coords = gs.Feature(geometry=gs.LineString(RP),
                properties={'label': 'Route #{}'.format(index+1), 'color': color})
            term = gs.Feature(geometry=gs.MultiPoint(
                (data.clusters[terminal[0]], data.clusters[terminal[1]]),
                properties={'label': 'Terminal #{}'.format(index+1), 'color': color}))
            index += 1
            features.append(coords)
            features.append(term)
        feature_r = gs.FeatureCollection([features])
        gs.dump(features, jfile)

if __name__ == '__main__':
    name, data_set = '35', range(2, 28+1, 2)
    data = Clusters()
    data.generateMatrix('./data/points.js', './data/ways.js')
    data.loadClusters('./data/clusters.js')
    for fset in data_set:
        file = './data_set/clusters-{}-{}.json'.format(name, fset)
        init_route = loadRoadNetwork(data, file)
        print('>> start processing `{}` file'.format(file))
        result = buildRoutes(data, init_route)
        dump_result(result, data, 'result-{}-{}.json'.format(name, fset))