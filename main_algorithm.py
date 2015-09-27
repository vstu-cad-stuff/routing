from data_loader import Clusters
from greedy_algorithm import greedyInit


# function: convert list to human readable format
# input:
#   lst -- array list
# output:
#   python list
def toHR(lst):
    return list(map(lambda x: x+1, lst))


# funciont: separation of the array with count parts
# input:
#   array -- input array
#   count -- parts count
# output:
#   python list
def toChunk(array, count):
    chunk_len = len(array) // count
    rest_count = len(array) % count
    chunks = []
    for i in range(count):
        chunk = array[:chunk_len]
        array = array[chunk_len:]
        if rest_count and array:
            chunk.append(array.pop(0))
            rest_count -= 1
        chunks.append(chunk)
    return chunks


# function: routes rating function
# input:
#   routes -- route network
# output:
#   ?
def routeRating(routes):
    pass


# function: mutation
# input:
#   ?
# output:
#   ?
def mutation():
    pass


# function: crossover
# input:
#   ?
# output:
#   ?
def crossover():
    pass


# function: generation of the route network, based on the greedy algorithm
# input:
#   route -- generated route by greedy algorithm
#   matrix -- correspondence matrix
# output:
#   python list of list -- [[route1], [route2], ...]
def buildRoutes(route, matrix):
    route_count = 5
    paths = toChunk(route, route_count)
    while routeRating(paths):
        pass
    pass

if __name__ == '__main__':
    data = Clusters()
    matrix = data.generateMatrix('./data/100_p.js', './data/ways.js')
    cluster = data.loadClusters('./data/100_c.js')
    init_route = greedyInit(matrix)
    result = buildRoutes(init_route, matrix)
    print(result)
