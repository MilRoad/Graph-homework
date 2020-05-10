import numpy
import time
from multiprocessing import Pool
from functools import partial


def dijkstra(adj_matrix, source_index):
    gr_order = len(adj_matrix)
    valid = [True] * gr_order
    weights = [1000000] * gr_order
    weights[source_index] = 0
    for i in range(gr_order):
        min_weight = 1000001
        min_weight_id = -1
        for j in range(gr_order):
            if valid[j] and weights[j] < min_weight:
                min_weight = weights[j]
                min_weight_id = j
        for z in range(gr_order):
            if weights[min_weight_id] + adj_matrix[min_weight_id][z] < weights[z]:
                weights[z] = weights[min_weight_id] + adj_matrix[min_weight_id][z]
        valid[min_weight_id] = False
    return weights


def compute(source_index, adj_matrix, actual_indexes):
    if source_index in actual_indexes:
        return dijkstra(adj_matrix, source_index)
    else:
        return adj_matrix[source_index]


def find_shortest_paths(adj_matrix, actual_indexes):
    short_adj_matrix = adj_matrix.copy()
    start = time.time()
    for i in actual_indexes:
        short_adj_matrix[i] = dijkstra(adj_matrix,i)
    end = time.time()
    print("Dijkstra: {0}".format(end-start))
    return short_adj_matrix


adj_matrix_example = [[i for i in range(3520)]] * 3520
actual_indexes_example = [i for i in range(110)]

find_shortest_paths(adj_matrix_example, actual_indexes_example)

# print(find_shortest_paths([[0, 40, 1000000, 1000000, 18],
#                 [40, 0, 22, 6, 15],
#                 [1000000, 22, 0, 14, 1000000],
#                 [1000000, 6, 14, 0, 20],
#                 [18, 15, 1000000, 20, 0]],[0,1,2]))
