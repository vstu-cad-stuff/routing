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
#   data  -- cluster data class (correspondence matrix, coordinates)
#   routes -- route network
# output:
#   [average distance, average traffic]
def routeRating(data, routes):
    total_distance = 0
    total_traffic = 0
    for route in routes:
        total_distance += data.getMetricCounter(data.getDistance, route)
        total_traffic += data.getMetricCounter(data.getPeople, route)
    return [total_distance / len(routes), total_traffic / len(routes)]


# function: swap two element
# input:
#   arr -- python list
#   i   -- first index
#   j   -- second index
# output:
#   None
def swapByIndex(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


# function: swap subarray
# input:
#   arr -- python list
#   i   -- first index
#   j   -- second index
# output:
#   None
def swapBySequence(arr, i, j):
    arr[i:j+1] = arr[i:j+1][::-1]


# function: sorting route by metric
# input:
#   metric -- 2-param metric python function
#       param #1 -- first cluster id
#       param #2 -- second cluster id
#   route  -- list of cluster_id
# output:
#   route  -- sorted list of cluster_id
def sortByMetric(metric, route):
    for index in range(len(route)-4):
        p1 = metric(route[index+0], route[index+1])
        p2 = metric(route[index+0], route[index+2])
        p3 = metric(route[index+1], route[index+2])
        if p1 > p3:
            swapByIndex(route, index+1, index+2)
        p1 = metric(route[index+0], route[index+3])
        p2 = metric(route[index+2], route[index+3])
        if p1 > p2:
            swapBySequence(route, index+0, index+3)


# function: find item in 'input' by func and move to 'output'
# input:
#   func   -- python function (max, min & etc)
#   data   -- information for comparison
#   input  -- source list (cluster_id)
#   output -- destination
# output:
#   None
def funcRemoveAppend(func, data, input, output):
    find = data.index(func(data))
    output.append(input[find])
    input.remove(input[find])