from re import sub, compile
import numpy as np

# compiled regex: select all chars ignore 0-9 and .
nonNumeric = compile(r'[^\d.]+')


# function: read data from file to string
# input:
#   filename -- file to read
# output:
#   string -- readed data
def readFile(filename):
    f = open(filename, 'r')
    buf = f.readlines()
    f.close()
    return buf


class Coords:
    # packed data
    packed = {}
    # cluster count
    max_cluster = 0

    # function: load raw data and add to dictionary
    # input:
    #   raw_points -- string with people data (coords and cluster)
    # output:
    #   None
    def loadRaw(self, raw_points):
        for string in raw_points:
            data = string.split(',')
            if len(data) < 4:
                continue
            index = int(nonNumeric.sub('', data[3]))
            self.max_cluster = max(index, self.max_cluster)
            self.append(float(data[1]), float(data[2]), index)

    # function: append cluster_id by coord hash
    # input:
    #   latitude -- first coord
    #   longitude -- second coord
    #   cluster -- cluster_id
    # output:
    #   None
    def append(self, latitude, longitude, cluster):
        hashMap = '{:0.010f}, {:0.010f}'.format(latitude, longitude)
        self.packed[hashMap] = cluster

    # function: find cluster_id by coord
    # input:
    #   latitude -- first coord
    #   longitude -- second coord
    # output:
    #   cluster_id
    def find(self, latitude, longitude):
        hashMap = '{:0.010f}, {:0.010f}'.format(latitude, longitude)
        return self.packed[hashMap]


class Clusters:
    matrix = None
    coords = Coords()
    clusters = {}

    # function: calculate correspondence matrix by coords & ways
    # input:
    #   coords   -- Coord class
    #   raw_ways -- movement data
    # output:
    #   None
    def calculateMatrix(self, coords, raw_ways):
        # init square matrix with max_cluster size
        self.matrix = np.zeros((self.coords.max_cluster+1, self.coords.max_cluster+1))
        # iterate ways data
        for string in raw_ways:
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

    # function: generate correspondence matrix by points & ways data
    # input:
    #   points -- filename with people coords
    #   ways   -- filename with people ways
    # output:
    #   numpy array -- correspondence matrix
    def generateMatrix(self, points, ways):
        # load raw data from points file
        self.coords.loadRaw(readFile(points))
        # and calculate correspondence matrix
        self.calculateMatrix(self.coords, readFile(ways))
        return self.matrix

    # function: load cluster data from file
    # input:
    #   file -- cluster coord data
    # output:
    #   dictionary[cluster_id] = [lat, lon]
    def loadClusters(self, file):
        data = readFile(file)[2].split(',')
        index = 0
        while index != len(data) - 3:
            lat = float(nonNumeric.sub('', data[index+0]))
            lon = float(nonNumeric.sub('', data[index+1]))
            cluster = int(nonNumeric.sub('', data[index+2]))
            self.clusters[cluster] = [lat, lon]
            index += 3
        return self.clusters
