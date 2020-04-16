import numpy as np


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


def find_shortest_paths(adj_matrix, actual_indexes):
    short_adj_matrix = adj_matrix.copy()
    for i in actual_indexes:
        short_adj_matrix[i] = dijkstra(adj_matrix, i)
    return short_adj_matrix


# если для дома под индексом 5 ближайшие больницы такие:
# "туда" имеет индекс 17 , "обратно" – 27 , "туда и обратно" – 37,
# то в возвращаемой матрице под индексом 5 будет находиться массив [17,27,37]
def find_nearest_hospitals_1a(dist_matrix, apart_count=100):
    nearest_hosp_list = [[-1 for i in range(3)] for j in range(apart_count)]
    for i in range(apart_count):
        nearest_hosp_list[i][0] = np.argmin(dist_matrix[i][apart_count:]) + apart_count
        nearest_hosp_list[i][1] = np.argmin(np.array(dist_matrix[apart_count:]).transpose()[i]) + apart_count
        tuda = dist_matrix[i][apart_count:]
        suda = np.array(dist_matrix[apart_count:]).transpose()[i]
        nearest_hosp_list[i][2] = np.argmin(tuda + suda) + apart_count
    return nearest_hosp_list


# возвращаемый список содержит списки с 3-мя списками индексов подходящих объектов:
# "туда", "обратно" и "туда и обратно" содержат своё количество индексов - это списки второго уровня,
# индекс списка первого уровня соответствует индексу дома во входной матрице расстояний. Например,
#
# [ [ [13,14,15],[],[33,35] ],
#   [ [22],[23,24],[25,99] ] ] означает:
# для дома с индексом 0
#     "туда" допустимы больницы с индексами 13, 14 и 15
#     "обратно" допустимых больниц нет
#     "туда и обратно" допустимы больницы 33 и 35
# для дома с индексом 1
#     "туда" допустима больница с индексом 22
#     "обратно" допустимы больницы 22 и 23
#     "туда и обратно" допустимы больницы 25 и 99
def find_in_radius_1b(dist_matrix, radius, apart_count=100):
    permissible_hosps = [[[] for i in range(3)] for j in range(apart_count)]
    for i in range(apart_count):
        for j in range(apart_count, len(dist_matrix)):
            if dist_matrix[i][j] <= radius:
                permissible_hosps[i][0].append(j)
            if dist_matrix[j][i] <= radius:
                permissible_hosps[i][1].append(j)
            if dist_matrix[i][j] + dist_matrix[j][i] <= radius:
                permissible_hosps[i][2].append(j)
    return permissible_hosps


# возвращаемый список содержит три больницы
# [ "туда", "обратно", "туда и обратно" ], где "туда" – из дома в больницу
def get_optimal_hospitals_2(dist_matrix, apart_count=100):
    optimal_hosps = []
    tuda = np.array(dist_matrix[:apart_count]).transpose()[apart_count:]
    optimal_hosps.append(np.argmin(np.amax(tuda, 1)) + apart_count)
    suda = np.array(dist_matrix[apart_count:])[:, :apart_count]
    optimal_hosps.append(np.argmin(np.amax(suda, 1)) + apart_count)
    tuda_suda = tuda + suda
    optimal_hosps.append(np.argmin(np.amax(tuda_suda, 1)) + apart_count)
    return optimal_hosps


# возвращается индекс больницы, для которой
# сумма расстояний от неё до всех домов минимальна
def min_sum_hosp_3(dist_matrix, apart_count=100):
    dist_sums = np.array(dist_matrix[apart_count:])[:, :apart_count]
    dist_sums = np.sum(dist_sums, 1)
    return np.argmin(dist_sums) + apart_count



# ===================== ТЕСТЫ =======================

# adj_matrix_example = [[i for i in range(3520)]] * 3520
# actual_indexes_example = [i for i in range(110)]
# print(find_shortest_paths(adj_matrix_example, actual_indexes_example))

print(find_shortest_paths([[0, 40, 1000000, 1000000, 18],
                           [40, 0, 22, 6, 15],
                           [1000000, 22, 0, 14, 1000000],
                           [1000000, 6, 14, 0, 20],
                           [18, 15, 1000000, 20, 0]], [0, 1, 2]))

print(find_nearest_hospitals_1a([[0, 2, 32, 30, 29],
                                 [1, 0, 13, 15, 15],
                                 [11, 25, 0, 1, 1],
                                 [12, 21, 1, 0, 1],
                                 [15, 22, 1, 1, 0]], 2))

print(find_in_radius_1b([[0, 1, 2, 3, 4],
                         [1, 0, 1, 5, 1],
                         [3, 2, 0, 1, 1],
                         [4, 3, 1, 0, 1],
                         [5, 3, 1, 1, 0]], 4, 2))

print(get_optimal_hospitals_2([[0, 1, 2, 3, 4],
                               [1, 0, 1, 15, 2],
                               [8, 20, 0, 1, 1],
                               [4, 3, 1, 0, 1],
                               [5, 3, 1, 1, 0]], 2))

print(min_sum_hosp_3([[0, 1, 2, 3, 4],
                      [1, 0, 1, 15, 2],
                      [8, 1, 0, 1, 1],
                      [4, 3, 1, 0, 1],
                      [5, 3, 1, 1, 0]], 2))
