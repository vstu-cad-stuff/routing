from functools import reduce
from auxiliary import swapByIndex
from randomcolor.randomcolor import RandomColor
from geographiclib.geodesic import Geodesic
from data_loader import Clusters
import numpy as np
import geojson as gs


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


class GeoConverter:
    def __init__(self, matrix):
        self.geo_data = None
        self.convex_hull = None
        self.outer_circle_points = None
        self.geo_center = None
        self.radius = None
        self.color_points = []
        self.matrix = matrix

    def load(self, filename):
        with open(filename, 'r') as jfile:
            self.geo_data = gs.load(jfile)
            return self
        raise Exception('data is not loaded')

    def dump(self, filename):
        with open(filename, 'w') as jfile:
            feature_convex = gs.Feature(
                geometry=gs.LineString(self.convex_hull),
                properties={'label': 'Convex Hull', 'color': '#1e90ff'})
            feature_center = gs.Feature(
                geometry=gs.Point(self.geo_center),
                properties={'label': 'Center of Convex Hull', 'color': '#B22222'})
            feature_pack = gs.FeatureCollection(
                [feature_convex, feature_center, self.geo_data])
            feature_color_point = gs.FeatureCollection(self.color_points)
            feature_outer_circle = gs.FeatureCollection(self.outer_circle_points)
            res_feature = gs.FeatureCollection([feature_pack, feature_color_point, feature_outer_circle])
            gs.dump(res_feature, jfile)
            return self
        raise Exception('can\'t write convex hull points to file')

    def graham(self):
        def rotate(d, a, b, c):
            return (d[b][1] - d[a][1]) * (d[c][0] - d[b][0]) - \
                (d[b][0] - d[a][0]) * (d[c][1] - d[b][1])
        coords = self.geo_data['coordinates']
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
        self.convex_hull = list(map(lambda x: coords[x], cluster_id))
        self.convex_hull.append(self.convex_hull[0])
        return self

    def center(self):
        length = len(self.geo_data['coordinates'])
        center_c1 = reduce(lambda x, y: x + y, map(lambda x: x[0], self.geo_data['coordinates'])) / length
        center_c2 = reduce(lambda x, y: x + y, map(lambda x: x[1], self.geo_data['coordinates'])) / length
        self.geo_center = [center_c1, center_c2]
        return self

    def pointInCircle(self, center):
        def it(data):
            for index in range(len(data)):
                yield [index, data[index]]
        initial_coeff = 0.05
        eps_multiplier = 1.5
        eps = self.radius * initial_coeff
        clusters = []
        while len(clusters) == 0:
            for index, item in it(self.geo_data['coordinates']):
                dist = getDistance(center, item)
                if dist < eps:
                    clusters.append(index)
            eps *= eps_multiplier
        return clusters

    def routes(self, count):
        distance = []
        r0 = self.geo_center
        for point in self.convex_hull:
            r1 = getDistance(r0, point)
            distance.append(r1)
        r1 = self.convex_hull[distance.index(max(distance))]
        self.radius = getDistance(r0, r1)
        self.outer_circle_points = []
        rnd_color = RandomColor()
        colors = rnd_color.generate(count=count)
        # color for clusters on the other side
        colors += colors
        ncount = np.arange(0, 360, 360/(2*count))
        for angle in ncount:
            data = getNewCoord(r0, angle, self.radius)
            self.outer_circle_points.append(
                gs.Feature(geometry=gs.Point(data), properties={
                    'label': 'Outer Circle Points', 'color': colors.pop()}))
        self.initial_cluster = []
        for item in self.outer_circle_points:
            points = self.pointInCircle(item['geometry']['coordinates'])
            # sort list by max people in cluster
            points.sort(key=lambda x: -matrix.getPeople(x, x))
            self.initial_cluster.append([
                points[0], item['geometry']['coordinates'],
                item['properties']['color']
            ])
        for found, cluster, color in self.initial_cluster:
            destination = self.geo_data['coordinates'][found]
            self.color_points.append(gs.Feature(
                geometry=gs.LineString([cluster, destination]),
                properties={'label': 'Initial clusters', 'color': color}))
        return self

if __name__ == '__main__':
    # badcode! please update!
    # rewrite data_loader module
    matrix = Clusters()
    matrix.generateMatrix('./data/100_p.js', './data/ways.js')
    data = GeoConverter(matrix)
    data.load('./data/geoJSON.json').graham().center().routes(12)
    data.dump('./convex-hull.json')
