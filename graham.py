from functools import reduce
from auxiliary import swapByIndex
from randomcolor.randomcolor import RandomColor
from geographiclib.geodesic import Geodesic
from data_loader import Clusters
import requests
import numpy as np
import geojson as gs
import json as js

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
        self.distance = self.distance()

    def distance(self):
        viaroute = SERVER_URL + 'viaroute?alt=false&geometry=false'
        for item in self.ids:
            viaroute += '&loc={},{}'.format(self.coord[item][1], self.coord[item][0])
        req = js.loads(requests.get(viaroute).text)
        return req['route_summary']['total_distance']

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
        return '[{}] {} : {}'.format(self.key, self.ids, self.distance)


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
        RN = []
        for A, B in C_t:
            RN.append(Route([A, B], self.geo_data))
        while C_nt:
            for index in range(N_r):
                # check `C_nt`
                if C_nt == []:
                    break
                # step 1
                R_i = RN[index]
                # step 2
                # странно работает
                PN = R_i.pairs()
                # step 3.1
                RC = []
                # step 3
                for n_x, n_y in PN:
                    NewRoutes = []
                    OldRoute = Route([n_x, n_y], self.geo_data)
                    # step 3.2
                    for j, c_j in itIndexData(C_nt):
                        NewRoutes.append(Route([n_x, c_j, n_y], self.geo_data, key=j))
                    # j = argmin(|len(n_x, n_y) - len(n_x, c_j, n_y)|)
                    NewRoutes.sort(key=lambda x: abs(OldRoute.distance-x.distance))
                    # step 3.3
                    RC.append(NewRoutes[0])
                # step 4 (modified)
                RCC = []
                for item in RC:
                    # get 'insert' node
                    add_node = item[1]
                    # find index `item` in R_i
                    idx = R_i.index(item[0]) + 1
                    # copy `R_i` data to `new_route`
                    new_route = R_i.ids
                    # insert `add_node` to `new_route`
                    new_route.insert(idx, add_node)
                    # add `new_route` to `RCC`
                    RCC.append(Route(new_route, self.geo_data, key=item.key))
                # step 5: sort by ascending
                RCC.sort(key=lambda x: x.distance)
                # step 6: replace `RN` element by `RCC`
                RN[index] = RCC[0]
                # step 7: remove `C_nt` element by `RCC` key (node indexing)
                del C_nt[RCC[0].key]
        return RN

if __name__ == '__main__':
    # badcode! please update!
    # rewrite data_loader module
    matrix = Clusters()
    matrix.generateMatrix('./data/100_p.js', './data/ways.js')
    data = GeoConverter(matrix)
    data.load('./data/geoJSON.json').graham().center()
    N_r = 12
    C_t, C_nt = data.findTerminals(N_r)
    RN = data.routing(N_r, C_t, C_nt)
    for index, data in itIndexData(RN):
        print('{:04} -- {}'.format(index, data))
    # data.dump('./convex-hull.json')
