from data_loader import Clusters
from greedy_algorythm import greedy_init


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
        items = array[chunk_len:]
        if rest_count and array:
            chunk.append(array.pop(0))
            rest_count -= 1
        chunks.append(chunk)
    return chunks

if __name__ == '__main__':
    data = Clusters()
    matrix = data.generate_matrix('./data/100_p.js', './data/ways.js')
    cluster = data.load_clusters('./data/100_c.js')
    lst = greedy_init(matrix)
    paths = toChunk(lst, 5)
