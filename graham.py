from functools import reduce
from auxiliary import swapByIndex
import geojson


class GeoConverter:
    def __init__(self):
        self.geo_data = None
        self.convex_hull = None
        self.geo_center = None

    def load(self, filename):
        with open(filename, 'r') as jfile:
            self.geo_data = geojson.load(jfile)
            return self
        raise Exception('data is not loaded')

    def dump(self, filename):
        with open(filename, 'w') as jfile:
            feature_convex = geojson.Feature(geometry=self.convex_hull, properties={'label': 'Convex hull'})
            feature_center = geojson.Feature(geometry=self.geo_center, properties={'label': 'Center of convex hull'})
            features = geojson.FeatureCollection([feature_convex, feature_center, self.geo_data])
            geojson.dump(features, jfile)
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
        convex_hull = list(map(lambda x: coords[x], cluster_id))
        convex_hull.append(convex_hull[0])
        self.convex_hull = geojson.LineString(convex_hull)
        return self

    def center(self):
        length = len(self.geo_data['coordinates'])
        center_c1 = reduce(lambda x, y: x + y, map(lambda x: x[0], self.geo_data['coordinates'])) / length
        center_c2 = reduce(lambda x, y: x + y, map(lambda x: x[1], self.geo_data['coordinates'])) / length
        self.geo_center = geojson.Point([center_c1, center_c2])
        return self

if __name__ == '__main__':
    data = GeoConverter()
    data.load('./data/geoJSON.json').graham().center().dump('./render-page/js/convex-hull.json')
