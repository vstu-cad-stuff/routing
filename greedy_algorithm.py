def findMax(A):
    """
    search node with the highest number of people

    input:
        A -- correspondence matrix
    output:
        n, m -- node index
    """
    max_a = A[0][0]
    n, m = 0, 0
    # a simple search on the entire array
    for i in range(1, len(A)):
        for j in range(i+1, len(A)):
            if A[j][i] > max_a:
                max_a = A[j][i]
                n, m = i, j
    return n, m


def maxInMatrix(n, m, A):
    """
    compare two nodes

    input:
        n -- first node
        m -- second node
        A -- correspondence matrix
    output:
        a sequence of nodes
    """
    if A[n] > A[m]:
        return n, m
    else:
        return m, n


def maxInList(n, A, path):
    """
    search maximum in list

    input:
        n -- node index
        A -- correspondence matrix
        path -- number of people in clusters (list)
    output:
        k -- index of maximum
    """
    lst = list(map(lambda x: x[n], A))
    for i in range(len(lst)):
        if i in path:
            lst[i] = 0
    max_a, k = lst[0], 0
    for i in range(len(lst)):
        if lst[i] > max_a and i not in path:
            max_a = lst[i]
            k = i
    return k


def greedyInit(matrix):
    """
    greedy algorithm

    input:
        matrix -- correspondence matrix
    output:
        path -- clusters traversal sequence (list)
    """
    from copy import deepcopy
    Node = []
    # the maximum length of the route - the size of the matrix
    length_of_route = len(matrix)
    # generate number of people in clusters
    for i in range(length_of_route):
        Node.append(matrix[i][i])
    # hard copy of correspondence matrix
    W = deepcopy(matrix)
    path = []
    # find output node
    n, m = findMax(matrix)
    # find a way out of it
    n, m = maxInMatrix(n, m, Node)
    # append to result list
    path.append(n)
    # note in the array node and edge
    Node[n] = W[n][m] = -1
    for i in range(length_of_route):
        # go to the next best node
        n = maxInList(n, matrix, path)
        # if peaks begin to repeat, then exit the loop
        if len(path) > 2 and path[-1] == path[-2] and path[-1] == n:
            # and take out the repetition from the list
            path.pop()
            path.pop()
            break
        # append to result list
        path.append(n)
    return path
