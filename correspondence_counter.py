#!/bin/env python
from re import sub
from sys import argv

mainRegex = "([^0-9.',]|\'.*\'|,$)"

# coords hash table class
class Coords:
    packed = {}
    def appendRawBlock(self, block):
        for item in block:
            self.appendRaw(item)
    def appendRaw(self, raw):
        lat, lng, i = float(raw[0]), float(raw[1]), int(raw[2])
        self.append(lat, lng, i)
    def findRaw(self, raw):
        lat, lng = float(raw[0]), float(raw[1])
        return self.find(lat, lng)
    def append(self, latitude, longitude, cluster):
        hashMap = '{:0.010f}, {:0.010f}'.format(latitude, longitude)
        self.packed[hashMap] = cluster
    def find(self, latitude, longitude):
        hashMap = '{:0.010f}, {:0.010f}'.format(latitude, longitude)
        return self.packed.get(hashMap)
    def findMaxCluster(self):
        return max(self.packed.values())

# load data from file
def loadData(filename):
    f = open(filename, 'r')
    buff = f.readlines()
    f.close()
    return buff

# split data to compatible format
def splitData(regex, data):
    buff = []
    for x in data:
        tmp = sub(regex, '', x)[1:].split(',')
        if len(tmp) > 1:
            buff.append(tmp)
    return buff

# write list to file
def writeToFile(filename, data, prefix=''):
    f = open(filename, 'w')
    if prefix != '':
        f.write(prefix)
    f.write('[')
    for item in data:
        f.write('{},\n'.format(item))
    f.write(']')
    f.close()

if __name__ == '__main__':
    if len(argv) < 3:
        print('usage: {} <points> <ways> <output>'.format(argv[0]))
        exit(0)
    # load points data
    points = splitData(mainRegex, loadData(argv[1]))
    # load ways data
    ways = splitData(mainRegex, loadData(argv[2]));
    # create coords hash map by loaded points
    coord = Coords()
    coord.appendRawBlock(points)
    # get cluster count
    maxCluster = coord.findMaxCluster() + 1
    # create correspondence
    matrix = [[0 for i in range(maxCluster)] for i in range(maxCluster)]
    # counting
    for item in ways:
        i, j = coord.findRaw(item[:2]), coord.findRaw(item[2:])
        if i != j:
            matrix[i][j] += 1
            matrix[j][i] += 1
        matrix[i][i] += 1
        matrix[j][j] += 1
    # write correspondence to file with prefix (for import to python)
    writeToFile(argv[3], matrix, 'G = ')