import numpy as np

def dijkstra(N, S, matrix):
    valid = [True]*N
    weight = [1000000]*N
    weight[S] = 0
    for i in range(N):
        min_weight = 1000001
        ID_min_weight = -1
        for j in range(N):
            if valid[j] and weight[j] < min_weight:
                min_weight = weight[j]
                ID_min_weight = j
                for z in range(N):
                    if weight[ID_min_weight] + matrix[ID_min_weight][z] < weight[z]:
                        weight[z] = weight[ID_min_weight] + matrix[ID_min_weight][z]
                        pred[z] = ID_min_weight
        valid[ID_min_weight] = False
    return weight


max = 1000000
A = [[max, 41, max, max, max, 29],
     [max, max, 51, max, 32, max],
     [max, max, max, 50, max, max],
     [45, max, max, max, max, 38],
     [max, max, 32, 36, max, max],
     [max, 29, max, max, 21, max]]

matrix = np.zeros((len(A), len(A)))


pred_dict = {}

for i in range(len(A)):
    pred = {}
    distance = dijkstra(len(A), i, A)
    # словарь предшественников следующего вида:
    # у каждого узла-корня есть список его детей,
    # а у каждого ребенка - его предок
    pred_dict[i] = pred
    for j in range(len(A)):
        matrix[i][j] = distance[j]

print(matrix)
d_matrix = [[0,1,1], [1,0,1], [1,1,0]]

import scipy.spatial.distance as ssd
distArray = ssd.squareform(d_matrix)
print(distArray)

n = len(matrix)
y = matrix[np.triu_indices(n,1)]
print(y)

