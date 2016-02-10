from functools import reduce
from auxiliary import swapByIndex
from randomcolor.randomcolor import RandomColor
from multiprocessing.dummy import Pool as ThreadPool
from geographiclib.geodesic import Geodesic
from polyline.codec import PolylineCodec
from data_loader import Clusters
from copy import deepcopy
import requests
import numpy as np
import geojson as gs
import json as js
import datetime as dt

SERVER_URL = 'http://oriole.strategway.com:5000/'


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


def itIndexData(data):
    for index in range(len(data)):
        yield [index, data[index]]


class Route:
    def __init__(self, ids, coord, key=0):
        self.coord = coord
        self.ids = ids
        self.key = key
        self.dist = self.distance()

    def distance(self):
        viaroute = SERVER_URL + 'viaroute?alt=false&geometry=false'
        for item in self.ids:
            viaroute += '&loc={},{}'.format(self.coord[item][1], self.coord[item][0])
        req = js.loads(requests.get(viaroute).text)
        return req['route_summary']['total_distance']

    def route(self):
        viaroute = SERVER_URL + 'viaroute?alt=false&geometry=true'
        for item in self.ids:
            viaroute += '&loc={},{}'.format(self.coord[item][1], self.coord[item][0])
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
            self.geo_data = gs.load(jfile)['coordinates']
            return self
        raise Exception('data is not loaded')

    def load_raw(self, filename):
        with open(filename, 'r') as jfile:
            self.geo_data = []
            raw_points = jfile.readlines()
            for string in raw_points:
                data = string.split(',')
                if len(data) < 3:
                    continue
                data_1 = float(data[1].replace('[', ''))
                data_0 = float(data[0].replace('[', ''))
                self.geo_data.append([data_1, data_0])
            return self
        raise Exception('data is not loaded')

    def dump(self, filename):
        with open(filename, 'w') as jfile:
            pass
            # # Need refactoring
            # feature_convex = gs.Feature(
            #     geometry=gs.LineString(self.convex_hull),
            #     properties={'label': 'Convex Hull', 'color': '#1e90ff'})
            # feature_center = gs.Feature(
            #     geometry=gs.Point(self.geo_center),
            #     properties={'label': 'Center of Convex Hull', 'color': '#B22222'})
            # feature_pack = gs.FeatureCollection(
            #     [feature_convex, feature_center, self.geo_data])
            # feature_color_point = gs.FeatureCollection(self.color_points)
            # feature_outer_circle = gs.FeatureCollection(self.outer_circle_points)
            # res_feature = gs.FeatureCollection([feature_pack, feature_color_point, feature_outer_circle])
            # gs.dump(res_feature, jfile)
            # return self
        raise Exception('can\'t write convex hull points to file')

    def graham(self):
        def rotate(d, a, b, c):
            return (d[b][1] - d[a][1]) * (d[c][0] - d[b][0]) - \
                (d[b][0] - d[a][0]) * (d[c][1] - d[b][1])
        coords = self.geo_data
        length = len(coords)
        index = sorted(range(length), key=lambda x: coords[x][0])
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
        return self.geo_data.index(obj)

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
            for index, item in itIndexData(self.geo_data):
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
        distance = []
        r0 = self.geo_center
        for point in self.convex_hull:
            r1 = getDistance(r0, self.geo_data[point])
            distance.append(r1)
        r1 = self.convex_hull[distance.index(max(distance))]
        self.radius = getDistance(r0, self.geo_data[r1])
        self.outer_circle_points = []
        ncount = np.arange(0, 360, 360/(2*Nr))
        for angle in ncount:
            data = getNewCoord(r0, angle, self.radius)
            self.outer_circle_points.append(data)
        self.initial_cluster = []
        removed = set()
        for p1, p2 in byPairs(self.outer_circle_points):
            c1 = self.pointInCircle(p1)
            c2 = self.pointInCircle(p2)
            # sort list by max people in cluster
            c1.sort(key=lambda x: -matrix.getPeople(x, x))
            c2.sort(key=lambda x: -matrix.getPeople(x, x))
            removed.add(c1[0])
            removed.add(c2[0])
            self.initial_cluster.append([c1[0], c2[0]])
        other_clusters = []
        for item in range(len(self.geo_data)):
            if item not in removed:
                other_clusters.append(item)
        return [self.initial_cluster, other_clusters]

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

        def async_worker(pool, iterator, func, data):
            thread_list = []
            result = []
            for item in iterator:
                # create job for new_route function
                thread = pool.apply_async(func, (item, data))
                # add thread in list
                thread_list.append(thread)
            for thread in thread_list:
                # get result of job
                result.append(thread.get())
            return result
        RN = []
        thread_list = []
        # create 8 threads
        pool = ThreadPool(processes=8)
        # create initialization routes
        RN = async_worker(pool, C_t, lambda a, b: Route(a, b), (self.geo_data))
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
                RC = async_worker(pool, PN, new_route, (C_nt, self.geo_data))
                # step 4
                RCC = async_worker(pool, RC, build_route, (R_i, self.geo_data))
                # step 5: sort by ascending
                RCC.sort(key=lambda x: x.dist)
                # step 6: replace `RN` element by `RCC`
                RN[index] = RCC[0]
                # step 7: remove `C_nt` element by `RCC` key (node indexing)
                del C_nt[RCC[0].key]
        pool.close()
        return RN


def dump(list_data, data, filename):
    with open(filename, 'w') as jfile:
        rnd_color = RandomColor()
        colors = rnd_color.generate(count=len(list_data))
        # print(colors)
        features = []
        index = 1
        features.append(gs.MultiPoint(data.geo_data))
        for item in list_data:
            color = colors.pop()
            terminal = [item[0], item[-1]]
            # get route coords by road
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
    route_name = [100, 150, 200, 300]
    matrix = Clusters()
    for name in route_name:
        for N_r in range(8, 20, 2):
            print('{} >> data {}_p.js for N_r count {}'.format(dt.datetime.now(), name, N_r))
            matrix.generateMatrix('./data/{}_p.js'.format(name), './data/ways.js')
            data = GeoConverter(matrix).load_raw('./data/{}_c.js'.format(name)).graham().center()
            print('{} >> data loaded ... ok'.format(dt.datetime.now()))
            C_t, C_nt = data.findTerminals(N_r)
            print('{} >> terminals founded ... ok'.format(dt.datetime.now()))
            RN = data.routing(N_r, C_t, C_nt)
            print('{} >> generated route ... ok'.format(dt.datetime.now()))
            for index, item in itIndexData(RN):
                print('{:04} -- {}'.format(index, item))
            print('{} >> data saved in ./article/result-{}-{}.json'.format(dt.datetime.now(), name, N_r))
            dump(RN, data, './article/result-{}-{}.json'.format(name, N_r))
