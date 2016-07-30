from functools import reduce
from auxiliary import swapByIndex
from randomcolor.randomcolor import RandomColor
from multiprocessing.dummy import Pool as ThreadPool
from geographiclib.geodesic import Geodesic
from polyline.codec import PolylineCodec
from data_loader import Clusters
from re import sub, compile
from copy import deepcopy
import requests
import numpy as np
import geojson as gs
import json as js
import datetime as dt
import sys
import os

# OSRM server
SERVER_URL = 'http://127.0.0.1:5000/'
THREAD_COUNT = 8

# thread THREAD_COUNT thread pool
POOL = ThreadPool(processes=THREAD_COUNT)

# function: calculate distance from a to b
# input:
#   a -- first point
#   b -- second point
# output:
#   distance in sphere
def getDistance(a, b):
    return Geodesic.WGS84.Inverse(a[1], a[0], b[1], b[0])['s12']


# function: calculate new point
# input:
#   a       -- point coord ([lon, lat]
#   azimut  -- ...
#   radius  -- ...
def getNewCoord(a, azimut, radius):
    lst = Geodesic.WGS84.Direct(a[1], a[0], azimut, radius)
    return [lst['lon2'], lst['lat2']]


def itIndexDict(data):
    for index in data.keys():
        yield [index, data[index]]


def itIndexData(data):
    for index in range(len(data)):
        yield [index, data[index]]


def async_worker(iterator, func, data):
    thread_list = []
    result = []
    for item in iterator:
        # create job for new_route function
        thread = POOL.apply_async(func, (item, data))
        # add thread in list
        thread_list.append(thread)
    for thread in thread_list:
        # get result of job
        result.append(thread.get())
    return result


class Route:
    def __init__(self, ids, coord, key=0, metric=1):
        self.coord = coord
        self.ids = ids
        self.key = key
        if metric == 0:
            self.dist = self.node()
        else:
            self.dist = self.distance()

    # graph metric
    def node(self):
        result_distance = 0
        for index in range(1, len(self.ids)):
            a = self.coord.get(self.ids[index-1])
            b = self.coord.get(self.ids[index+0])
            result_distance += getDistance(a, b)
        return result_distance

    # osrm metric
    def distance(self):
        viaroute = SERVER_URL + 'viaroute?alt=false&geometry=false'
        for item in self.ids:
            try:
                coords = self.coord.get(item)
                viaroute += '&loc={},{}'.format(coords[1], coords[0])
            except:
                print('>> note {} not found!'.format(item))
                sys.exit()
        req = js.loads(requests.get(viaroute).text)
        return req['route_summary']['total_distance']

    # route with geometry
    def route(self):
        viaroute = SERVER_URL + 'viaroute?alt=false&geometry=true'
        for item in self.ids:
            try:
                coords = self.coord.get(item)
                viaroute += '&loc={},{}'.format(coords[1], coords[0])
            except:
                print('>> note {} not found!'.format(item))
                sys.exit()
        req = js.loads(requests.get(viaroute).text)
        return list(map(
            lambda x: [x[1] / 10.0, x[0] / 10.0], PolylineCodec().decode(req['route_geometry'])
        ))

    def __getitem__(self, index):
        return self.ids[index]

    def __setitem__(self, index, value):
        self.ids[index] = value

    def index(self, value):
        return self.ids.index(value)

    def insert(self, index, value):
        self.ids.insert(index, value)

    def pairs(self):
        pair = []
        for index in range(len(self.ids)-1):
            pair.append([self.ids[index+0], self.ids[index+1]])
        return pair

    def __str__(self):
        return '[{}] {} : {}'.format(self.key, self.ids, self.dist)


class GeoConverter:
    def __init__(self, matrix):
        self.geo_data = None
        self.convex_hull = None
        self.outer_circle_points = None
        self.geo_center = None
        self.radius = None
        self.route_points = []
        self.matrix = matrix

    def load(self, filename):
        with open(filename, 'r') as jfile:
            i = 0
            for item in gs.load(jfile)['coordinates']:
                self.geo_data[i] = item
                i += 1
            return self
        raise Exception('data is not loaded')

    def load_json(self, filename):
        with open(filename, 'r') as jfile:
            self.geo_data = {}
            points = js.load(jfile)
            for p in points:
                self.geo_data[p['id']] = (p['lon'], p['lat'])
            # for string in raw_points:
            #     data = string.split(',')
            #     if len(data) < 3:
            #         continue
            #     data_2 = int(data[2].replace(']', ''))
            #     data_1 = float(data[1].replace('[', ''))
            #     data_0 = float(data[0].replace('[', ''))
            #     self.geo_data[data_2] = [data_1, data_0]
            return self
        raise Exception('data is not loaded')

    def graham(self):
        def rotate(d, a, b, c):
            return (d[b][1] - d[a][1]) * (d[c][0] - d[b][0]) - \
                (d[b][0] - d[a][0]) * (d[c][1] - d[b][1])
        coords = self.geo_data
        length = len(coords)
        index = sorted(coords.keys(), key=lambda x: coords[x][0])
        for i in range(2, length):
            j = i
            while (j > 1) and (rotate(coords, index[0], index[j-1], index[j]) < 0):
                swapByIndex(index, j, j-1)
                j -= 1
        cluster_id = [index[0], index[1]]
        for i in range(2, length):
            while rotate(coords, cluster_id[-2], cluster_id[-1], index[i]) < 0:
                del cluster_id[-1]
            cluster_id.append(index[i])
        self.convex_hull = cluster_id
        return self

    def findCluster(self, obj):
        return list(self.geo_data.keys())[list(self.geo_data.values()).index(obj)]

    def indexToCoord(self, obj):
        route = []
        for index in obj:
            route.append(self.geo_data[index])
        return route

    def coordToIndex(self, obj):
        route = []
        for coord in obj:
            route.append(self.findCluster(coord))
        return route

    def center(self):
        length = len(self.convex_hull)
        center_c1 = reduce(lambda x, y: x + y, map(
            lambda x: self.geo_data[x][0], self.convex_hull)) / length
        center_c2 = reduce(lambda x, y: x + y, map(
            lambda x: self.geo_data[x][1], self.convex_hull)) / length
        self.geo_center = [center_c1, center_c2]
        return self

    def pointInCircle(self, center):
        initial_coeff = 0.05
        eps_multiplier = 1.5
        eps = self.radius * initial_coeff
        clusters = []
        while len(clusters) == 0:
            for index, item in itIndexDict(self.geo_data):
                dist = getDistance(center, item)
                if dist < eps:
                    clusters.append(index)
            eps *= eps_multiplier
        return clusters

    def findTerminals(self, Nr):
        def byPairs(a):
            mid = len(a) // 2
            for index in range(mid):
                yield [a[index], a[index+mid]]

        def pairing(item, etc):
            p1, p2 = item
            c1 = etc.pointInCircle(p1)
            c2 = etc.pointInCircle(p2)
            # sort list by max people in cluster
            c1.sort(key=lambda x: -matrix.getPeople(x, x))
            c2.sort(key=lambda x: -matrix.getPeople(x, x))
            return [c1[0], c2[0]]

        r0 = self.geo_center
        distance = async_worker(self.convex_hull, lambda a, b: getDistance(r0, b[a]), (self.geo_data))
        r1 = self.convex_hull[distance.index(max(distance))]
        self.radius = getDistance(r0, self.geo_data[r1])
        self.outer_circle_points = []
        ncount = np.arange(0, 360, 360/(2*Nr))
        self.outer_circle_points = async_worker(ncount, lambda a, b: getNewCoord(b[0], a, b[1]), (r0, self.radius))
        self.initial_cluster = async_worker(byPairs(self.outer_circle_points), pairing, (self))
        remove = set()
        for item in self.initial_cluster:
            remove.add(item[0])
            remove.add(item[1])
        other_clusters = []
        for item in self.geo_data.keys():
            if item not in remove:
                other_clusters.append(item)
        return self.initial_cluster, other_clusters

    def routing(self, N_r, C_t, C_nt):
        def new_route(item, etc):
            NewRoutes = []
            # unpacking data
            C_nt, geo_data = etc[0], etc[1]
            n_x, n_y = item[0], item[1]
            OldRoute = Route([n_x, n_y], geo_data)
            # step 3.2
            for j, c_j in itIndexData(C_nt):
                NewRoutes.append(Route([n_x, c_j, n_y], geo_data, key=j))
            # j = argmin(|len(n_x, n_y) - len(n_x, c_j, n_y)|)
            NewRoutes.sort(key=lambda x: abs(OldRoute.dist-x.dist))
            # step 3.3
            return NewRoutes[0]

        def build_route(item, etc):
            R_i, geo_data = etc[0], etc[1]
            # get 'insert' node from RC: [item[0], >>item[1]<<, item[2]]
            add_node = item[1]
            # find index `item` in R_i: [.., item[0], item[2], ...]
            idx = R_i.index(item[0]) + 1
            # hard copy `R_i` data to `new_route`
            new_route = deepcopy(R_i.ids)
            # insert `add_node` to `new_route`
            new_route.insert(idx, add_node)
            # add `new_route` to `RCC`
            return Route(new_route, geo_data, key=item.key)

        RN = []
        thread_list = []
        # create initialization routes
        RN = async_worker(C_t, lambda a, b: Route(a, b), (self.geo_data))
        while C_nt:
            for index in range(N_r):
                # check `C_nt`
                if C_nt == []:
                    break
                # step 1 (hard copy)
                R_i = deepcopy(RN[index])
                # step 2
                PN = R_i.pairs()
                # step 3, 3.1, 3.3
                RC = async_worker(PN, new_route, (C_nt, self.geo_data))
                # step 4
                RCC = async_worker(RC, build_route, (R_i, self.geo_data))
                # step 5: sort by ascending
                RCC.sort(key=lambda x: x.dist)
                # step 6: replace `RN` element by `RCC`
                RN[index] = RCC[0]
                # step 7: remove `C_nt` element by `RCC` key (node indexing)
                del C_nt[RCC[0].key]
        return RN


def dump(list_data, data, filename, geometry='route'):
    with open(filename, 'w') as jfile:
        rnd_color = RandomColor()
        colors = rnd_color.generate(count=len(list_data))
        features = []
        index = 1
        features.append(gs.MultiPoint(list(data.geo_data.values())))
        for item in list_data:
            color = colors.pop()
            terminal = [item[0], item[-1]]
            # get route coords by road
            if geometry == 'graph':
                # graph geometry
                RP = data.indexToCoord(item)
            else:
                # osrm geometry
                RP = item.route()
            coords = gs.Feature(geometry=gs.LineString(RP),
                properties={'label': 'Route #{}'.format(index+1), 'color': color})
            term = gs.Feature(geometry=gs.MultiPoint(data.indexToCoord(terminal)),
                properties={'label': 'Terminal #{}'.format(index+1), 'color': color})
            index += 1
            features.append(coords)
            features.append(term)
        feature_r = gs.FeatureCollection([features])
        gs.dump(features, jfile)

if __name__ == '__main__':
    name = '35'
    N_count = range(2, 28+1, 2)
    route_dist = []
    matrix = Clusters()
    print('{} >> loading data points.js'.format(dt.datetime.now()))
    matrix.generateMatrix('./data/points.js', './data/ways.js')
    data = GeoConverter(matrix).load_json('./data/clusters.js').graham().center()
    print('{} >> data loaded ... ok'.format(dt.datetime.now()))
    for N_r in N_count:
        if not os.path.isdir('article'):
            os.mkdir('article')
        terminals_file = 'article/info-{}-{}.out'.format(name, N_r)
        if not os.path.isfile(terminals_file):
            C_t, C_nt = data.findTerminals(N_r)
            with open(terminals_file, 'w') as f:
                f.write('C_t = {}\n'.format(C_t))
                f.write('C_nt = {}\n'.format(C_nt))
        else:
            def readAndSplit(f, data_type, extend=False):
                result = []
                nonNumeric = compile(r'[^0-9,]')
                data = nonNumeric.sub('', f.readline()).split(',')
                if not extend:
                    while data:
                        two, one = data.pop(), data.pop()
                        result.append([data_type(one), data_type(two)])
                    result.reverse()
                else:
                    result = list(map(lambda x: data_type(x), data))
                return result
            with open(terminals_file, 'r') as f:
                C_t = readAndSplit(f, int)
                C_nt = readAndSplit(f, int, extend=True)
        print('{} >> {} terminals founded ... ok'.format(dt.datetime.now(), N_r))
        RN = data.routing(N_r, C_t, C_nt)
        print('{} >> generated route ... ok'.format(dt.datetime.now()))
        current = []
        for index, item in itIndexData(RN):
            print('{:04} -- {}'.format(index, item))
            current.append(item.dist)
        print('{} >> data saved in ./article/result-{}-{}.json'.format(dt.datetime.now(), name, N_r))
        dump(RN, data, './article/result-{}-{}.json'.format(name, N_r))
        route_dist.append(current)
    with open('distances.js', 'w') as fp:
        fp.write('distances = [')
        for item in route_dist:
            fp.write('{},\n'.format(item))
        fp.write('];')
    POOL.close()
