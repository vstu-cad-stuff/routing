from functools import reduce
from auxiliary import swapByIndex
import numpy as np
import geojson as gs


# function: calculate distance from a to b
# input:
#   a -- first point (cluster_id)
#   b -- second point (cluster_id)
# output:
#   distance in sphere
def getDistance(a, b):
    # sphere radius (Earth) in meters
    rad = 6372795
    dlng = abs(a[0] - b[0]) * np.pi / 180.0
    lat1, lat2 = a[1] * np.pi / 180.0, b[1] * np.pi / 180.0
    p1, p2, p3 = np.cos(lat2), np.sin(dlng), np.cos(lat1)
    p4, p5, p6 = np.sin(lat2), np.sin(lat1), np.cos(dlng)
    y = np.sqrt(np.power(p1 * p2, 2) + np.power(p3 * p4 - p5 * p1 * p6, 2))
    x = p5 * p4 + p3 * p1 * p6
    return rad * np.arctan2(y, x)


class GeoConverter:
    def __init__(self):
        self.geo_data = None
        self.convex_hull = None
        self.circle_points = None
        self.radius = None
        self.geo_center = None

    def load(self, filename):
        with open(filename, 'r') as jfile:
            self.geo_data = gs.load(jfile)
            return self
        raise Exception('data is not loaded')

    def dump(self, filename):
        with open(filename, 'w') as jfile:
            feature_convex = gs.Feature(
                geometry=gs.LineString(self.convex_hull),
                properties={'label': 'Convex hull'})
            feature_center = gs.Feature(
                geometry=gs.Point(self.geo_center),
                properties={'label': 'Center of convex hull'})
            feature_points = gs.Feature(
                geometry=gs.LineString(self.circle_points),
                properties={'label': 'Convex Hull points'})
            features = gs.FeatureCollection(
                [feature_convex, feature_center, self.geo_data, feature_points])
            gs.dump(features, jfile)
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

    def routes(self, count):
        distance = []
        r0 = self.geo_center
        for point in self.convex_hull:
            r1 = getDistance(r0, point)
            distance.append(r1)
        radius_point = self.convex_hull[distance.index(max(distance))]
        self.radius = [abs(r0[0]-radius_point[0]), abs(r0[1]-radius_point[1])]
        self.circle_points = []
        for angle in range(0, 360, 10):
            angle_rad = angle * np.pi / 180
            # radius = self.radius[0] if self.radius[0] > self.radius[1] else self.radius[1]
            radius = np.sqrt(self.radius[0] ** 2 + self.radius[1] ** 2)
            point = [
                r0[0] + radius * np.cos(angle_rad),
                r0[1] + radius * np.sin(angle_rad)
            ]
            tmp = np.sqrt((r0[0]-point[0]) ** 2 + (r0[1]-point[1]) ** 2)
            print(getDistance(r0, point), tmp)

            self.circle_points.append(point)
        self.circle_points.append(self.circle_points[0])
        return self

if __name__ == '__main__':
    data = GeoConverter()
    data.load('./data/geoJSON.json').graham().center().routes(25)
    data.dump('./convex-hull.json')
