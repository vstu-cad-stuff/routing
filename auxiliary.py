def toHR(lst):
    """
    convert list to human readable format
    input:
        lst -- array list
    output:
        python list
    """
    return list(map(lambda x: x+1, lst))


def toChunk(array, count):
    """
    separate array with count parts
    input:
        array -- input array
        count -- parts count
    output:
        python list
    """
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


def routeRating(data, routes):
    """
    route rating function
    input:
        data  -- cluster data class (correspondence matrix, coordinates)
        routes -- route network
    output:
        (average distance, average traffic)
    """
    total_distance = 0
    total_traffic = 0
    for route in routes:
        total_distance += data.getMetricCounter(data.getOSRMDistance, route)
        total_traffic += data.getMetricCounter(data.getPeople, route)
    return total_traffic / total_distance


def swapByIndex(arr, i, j):
    """
    swap elements by index
    input:
        arr -- python list
        i   -- first index
        j   -- second index
    output:
        None
    """
    arr[i], arr[j] = arr[j], arr[i]


def swapBySequence(arr, i, j):
    """
    swap subarray items by index
    input:
        arr -- python list
        i   -- first index
        j   -- second index
    output:
        None
    """
    arr[i:j+1] = arr[i:j+1][::-1]


def sortByMetric(metric, route):
    """
    sort route by metric
    input:
        metric -- 2-param metric python function
            param #1 -- first cluster id
            param #2 -- second cluster id
        route  -- list of cluster_id
    output:
        route  -- sorted list of cluster_id
    """
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


def funcRemoveAppend(func, data, input, output):
    """
    find item in 'input' by func and move to 'output'
    input:
        func   -- python function (max, min & etc)
        data   -- information for comparison
        input  -- source list (cluster_id)
        output -- destination
    output:
        None
    """
    find = data.index(func(data))
    output.append(input[find])
    input.remove(input[find])