from geographiclib.geodesic import Geodesic
from re import sub, compile
import numpy as np
import json as js
import requests

# compiled regex: select all chars ignore 0-9 and .
nonNumeric = compile(r'[^\d.]+')

OSRM_SERVER_URL = 'http://127.0.0.1:5000/'

def readFile(filename):
    """
    read data from file to string

    input:
        filename -- file to read
    output:
        string -- readed data
    """
    f = open(filename, 'r')
    buf = f.readlines()
    f.close()
    return buf


class Coords:
    def __init__(self):
        # packed data
        self.packed = {}
        # cluster count
        self.max_cluster = 0

    def loadJSON(self, points):
        """
        load json data and add to dictionary

        input:
            points -- input file with coords and cluster data
        output:
            None
        """
        with open(points, 'r') as fp:
            data = js.load(fp)
            for item in data:
                index = item['clusterId']
                self.max_cluster = max(index, self.max_cluster)
                self.append(item['lat'], item['lon'], index)
        # for string in raw_points:
        #     data = string.split(',')
        #     if len(data) < 4:
        #         continue
        #     index = int(nonNumeric.sub('', data[3]))
        #     self.max_cluster = max(index, self.max_cluster)
        #     self.append(float(data[1]), float(data[2]), index)

    def append(self, latitude, longitude, cluster):
        """
        append cluster_id by coord hash

        input:
            latitude -- first coord
            longitude -- second coord
            cluster -- cluster_id
        output:
            None
        """
        hashMap = '{:0.010f}, {:0.010f}'.format(latitude, longitude)
        self.packed[hashMap] = cluster

    def find(self, latitude, longitude):
        """
        find cluster_id by coord

        input:
            latitude -- first coord
            longitude -- second coord
        output:
            cluster_id        
        """
        hashMap = '{:0.010f}, {:0.010f}'.format(latitude, longitude)
        return self.packed[hashMap]


class Clusters:
    def __init__(self):
        self.matrix = None
        self.coords = Coords()
        self.clusters = {}

    def calculateMatrix(self, coords, raw_ways):
        """
        calculate correspondence matrix by coords & ways

        input:
            coords   -- Coord class
            raw_ways -- movement data
        output:
            None
        """
        # init square matrix with max_cluster size
        self.matrix = np.zeros((self.coords.max_cluster+1, self.coords.max_cluster+1))
        with open(raw_ways, 'r') as f:
            # iterate by ways data
            for string in f:
                data = string.split(',')
                # ignore uncorrect data
                if len(data) < 5:
                    continue
                # parse & convert to float
                p1 = float(nonNumeric.sub('', data[1]))
                p2 = float(nonNumeric.sub('', data[2]))
                p3 = float(nonNumeric.sub('', data[3]))
                p4 = float(nonNumeric.sub('', data[4]))
                # find cluster_id by coords
                i, j = self.coords.find(p1, p2), self.coords.find(p3, p4)
                # increment cluster matrix
                self.matrix[i][j] += 1
                self.matrix[j][i] += 1
                self.matrix[i][i] += 1
                self.matrix[j][j] += 1

    def generateMatrix(self, points, ways):
        """
        generate correspondence matrix by points & ways data

        input:
            points -- filename with people coords
            ways   -- filename with people ways
        output:
            numpy array -- correspondence matrix
        """
        # load raw data from points file
        self.coords.loadJSON(points)
        # and calculate correspondence matrix
        self.calculateMatrix(self.coords, ways)
        return self.matrix

    def loadClusters(self, file):
        """
        load cluster data from file
    
        input:
            file -- cluster coord data
        output:
            dictionary[cluster_id] = [lat, lon]
        """
        for item in readFile(file):
            data = item.split(',')
            if len(data) < 3:
                continue
            lat = float(nonNumeric.sub('', data[0]))
            lon = float(nonNumeric.sub('', data[1]))
            cluster = int(nonNumeric.sub('', data[2]))
            self.clusters[cluster] = [lat, lon]
        return self.clusters

    def getSphereDistance(self, a, b):
        """
        calculate distance from a to b
    
        input:
            a -- first point (cluster_id)
            b -- second point (cluster_id)
        output:
            distance on the sphere
        """
        p1, p2 = self.clusters[a], self.clusters[b]
        return Geodesic.WGS84.Inverse(p1[1], p1[0], p2[1], p2[0])['s12']

    def getOSRMDistance(self, a, b):
        """
        calculate distance from a to b
    
        input:
            a -- first point (cluster_id)
            b -- second point (cluster_id)
        output:
            distance on the road network
        """
        p1, p2 = self.clusters[a], self.clusters[b]
        viaroute = OSRM_SERVER_URL + 'viaroute?alt=false&geometry=false'
        viaroute += '&loc={},{}&loc={},{}'.format(p1[1], p1[0], p2[1], p2[0])
        req = js.loads(requests.get(viaroute).text)
        return req['route_summary']['total_distance']

    def getPeople(self, a, b):
        """
        calculate people count from a to b

        input:
            a -- first point (cluster_id)
            b -- second point (cluster_id)
        output:
            people count
        """
        return self.matrix[a][b]

    def getMetricCounter(self, func, route):
        """
        calculate route param by func from cluster_id list

        input:
            func  -- calculation func (getPeople, getDistance)
            route -- array of cluster_id
        ouput:
            route param
        """
        param = 0
        for index in range(len(route)-1):
            param += func(route[index+0], route[index+1])
        return param
