# function: search node with the highest number of people
# input:
#   A -- correspondence matrix
# output:
#   n, m -- node index
def find_max(A):
    max_a = A[0][0]
    n, m = 0, 0
    # a simple search on the entire array
    for i in range(1, len(A)):
        for j in range(i+1, len(A)):
            if A[j][i] > max_a:
                max_a = A[j][i]
                n, m = i, j
    return n, m


# function: compare two nodes
# input:
#   n -- first node
#   m -- second node
#   A -- correspondence matrix
# output:
#   a sequence of nodes
def max_in_matrix(n, m, A):
    if A[n] > A[m]:
        return n, m
    else:
        return m, n


# function: search maximum in list
# input:
#   n -- node index
#   A -- correspondence matrix
#   path -- number of people in clusters (list)
def max_in_list(n, A, path):
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


# function: greedy algorythm
# input:
#   matrix -- correspondence matrix
# output:
#   path -- clusters traversal sequence (list)
def greedy_init(matrix):
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
    n, m = find_max(matrix)
    # find a way out of it
    n, m = max_in_matrix(n, m, Node)
    # append to result list
    path.append(n)
    # note in the array node and edge
    Node[n] = W[n][m] = -1
    for i in range(length_of_route):
        # go to the next best node
        n = max_in_list(n, matrix, path)
        # if peaks begin to repeat, then exit the loop
        if len(path) > 2 and path[-1] == path[-2] and path[-1] == n:
            # and take out the repetition from the list
            path.pop()
            path.pop()
            break
        # append to result list
        path.append(n)
    return path
