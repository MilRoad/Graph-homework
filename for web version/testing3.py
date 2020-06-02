# эта функция находит больницы, которые расположены так, что время/расстояние между ними и
# самым дальним домом минимально (“туда”, “обратно”, “туда и обратно”).

# функция возвращает координаты трех точек(больниц) в списке в следующей последовательности:
# координата больницы для "туда", координата больницы для "обратно", координата больницы для "туда обратно"
# эти точки как-нибудь изобразить на карте
def get_optimal_hospitals_2(dist_matrix, apart_count=100):
    # везде на вход матрица кратчайших расстояний и количество домов!
    optimal_hosps = []
    tuda = np.array(dist_matrix[:apart_count]).transpose()[apart_count:]
    optimal_hosps.append(np.argmin(np.amax(tuda, 1)) + apart_count)
    suda = np.array(dist_matrix[apart_count:])[:, :apart_count]
    optimal_hosps.append(np.argmin(np.amax(suda, 1)) + apart_count)
    tuda_suda = tuda + suda
    optimal_hosps.append(np.argmin(np.amax(tuda_suda, 1)) + apart_count)

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    hosp1 = numbers_of_nodes['hosp']['number_to_id'][str(optimal_hosps[0])]
    hosp2 = numbers_of_nodes['hosp']['number_to_id'][str(optimal_hosps[1])]
    hosp3 = numbers_of_nodes['hosp']['number_to_id'][str(optimal_hosps[2])]

    hosp1_c = coordinates['hosp'][hosp1]
    hosp2_c = coordinates['hosp'][hosp2]
    hosp3_c = coordinates['hosp'][hosp3]

    optimal_hosps_c = []
    optimal_hosps_c.append(hosp1_c)
    optimal_hosps_c.append(hosp2_c)
    optimal_hosps_c.append(hosp3_c)

    return optimal_hosps_c


# здесь возвращается одна больница, для которой сумма кратчайших расстояний от нее до всех
# домов минимальна.

# координаты одной больницы
def min_sum_hosp_3(dist_matrix, apart_count=100):
    dist_sums = np.array(dist_matrix[apart_count:])[:, :apart_count]
    dist_sums = np.sum(dist_sums, 1)

    hosp = np.argmin(dist_sums) + apart_count

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    hosp1 = numbers_of_nodes['hosp']['number_to_id'][str(hosp)]

    hosp1_c = coordinates['hosp'][hosp1]

    return hosp1_c

# возвращает больницу, для которой дерево кратчайших путей минимально
# в качестве аргумента нудно передать количество домов

# координаты больницы
def short_tree_4(N2):
    with open('numbers_of_nodes.json.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    aparts = list(numbers_of_nodes['apart']['number_to_id'].values())

    hosps = list(numbers_of_nodes['hosp']['number_to_id'].values())

    end_points = []
    trees_len = []
    for i in hosps:
        short_tree_len = 0
        for j in aparts:
            route = nx.shortest_path(G,
                                     int(i),
                                     int(j),
                                     weight='length')
            for temp in range(len(route) - 1):
                if route[temp] not in end_points:
                    short_tree_len += G_pd[nodes_numbers[str(route[temp])]][nodes_numbers[str(route[temp + 1])]]
                    end_points.append(route[temp])
        trees_len.append(short_tree_len)

    minimal = trees_len[0]
    hosp_n = 0
    for i in range(len(trees_len)):
        if trees_len[i] < minimal:
            minimal = trees_len[i]
            hosp_n = i

    hosp = numbers_of_nodes['hosp']['number_to_id'][str(hosp_n + N2)]

    hosp_c = coordinates['hosp'][hosp]

    return hosp_c