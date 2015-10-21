#!/bin/env python
import geojson


class GeoConverter:
    def __init__(self):
        self.geo_data = None
        self.convex_hull = None

    def load(self, filename):
        with open(filename, 'r') as jfile:
            self.geo_data = geojson.load(jfile)
            return self
        raise Exception('data is not loaded')

    def dump(self, filename):
        with open(filename, 'w') as jfile:
            feature = geojson.Feature(geometry=self.convex_hull),
            geojson.dump(feature, jfile)
            return self
        raise Exception('can\'t write convex hull points to file')

    def graham(self):
        def rotate(a, b, c):
            return (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
        a = self.geo_data['coordinates']
        n = len(a)
        p = list(range(n))
        for i in range(1, n):
            if a[p[i]][1] < a[p[0]][1]:
                p[0], p[i] = p[i], p[0]
        for i in range(2, n):
            j = i
            while (j > 1) and (rotate(a[p[0]], a[p[j - 1]], a[p[j]]) < 0):
                p[j], p[j - 1] = p[j - 1], p[j]
                j -= 1
        s = [p[0], p[1]]
        for i in range(2, n):
            while rotate(a[s[-2]], a[s[-1]], a[p[i]]) < 0:
                del s[-1]
            s.append(p[i])
        convex_hull = list(map(lambda x: a[x], s))
        convex_hull.append(convex_hull[0])
        self.convex_hull = geojson.LineString(convex_hull)
        return self

if __name__ == '__main__':
    data = GeoConverter()
    data.load('./data/geoJSON.json').graham().dump('./render-page/js/convex-hull.json')