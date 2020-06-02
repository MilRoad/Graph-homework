import osmnx as ox
import json
from random import randint
import networkx as nx
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import numpy as np

place = {'city': 'Kazan',
             'country': 'Russia'}
G = ox.graph_from_place(place, network_type='drive')

def choose_apartments(N, G):
    buildings = ox.footprints.footprints_from_place(place, footprint_type='building', retain_invalid=False,
                                                    which_result=1)

    hospitals = []
    apartmentss = []
    n = 10000
    build = buildings.head(n)['building'].to_dict()

    for key, value in build.items():
        if value == 'hospital':
            hospitals.append(key)
        elif value == 'apartments':
            apartmentss.append(key)

    # реализация рандомного выбора
    hospital = hospitals[randint(0, len(hospitals) - 1)]
    apartments = []
    for i in range(N):
        temp = apartmentss[randint(0, len(apartmentss) - 1)]
        if temp not in apartments:
            apartments.append(temp)

    # теперь берем координаты и находим ближайшие узлы

    a = buildings.head(n).to_dict()
    hospitals_dict = {}
    apartments_dict = {}

    coordinates = []

    bounds = a['geometry'][hospital].bounds
    temp = []
    x = (bounds[1] + bounds[3]) / 2
    y = (bounds[0] + bounds[2]) / 2
    temp.append(x)
    temp.append(y)
    nearest_node = ox.get_nearest_node(G, (x, y))
    hospitals_dict[str(nearest_node)] = temp
    coordinates.append(temp)

    for i in apartments:
        bounds = a['geometry'][i].bounds
        temp = []
        x = (bounds[1] + bounds[3]) / 2
        y = (bounds[0] + bounds[2]) / 2
        temp.append(x)
        temp.append(y)
        nearest_node = ox.get_nearest_node(G, (x, y))
        apartments_dict[str(nearest_node)] = temp
        coordinates.append(temp)

    dict_for_items = {}
    dict_for_items['hosp'] = hospitals_dict
    dict_for_items['apart'] = apartments_dict

    with open('coordinates.json', 'w') as f:
        json.dump(dict_for_items, f)

    return coordinates


# здесь считаю матрицу расстояний G_pd
# и еще важный словарь nodes_numbers

b = G.adj
dictionary = {}
i = 0
for key, value in b.items():
    if i == 10:
        break
    for key_a, value_a in value.items():

        if key not in dictionary:
            dictionary[key] = [{key_a: value_a[0]['length']}]
        else:
            dictionary[key].append({key_a: value_a[0]['length']})

nodes_list = list(G.nodes())
G_pd = nx.to_pandas_adjacency(G)
G_pd = G_pd.values

for i in range(len(G_pd)):
    for j in range(len(G_pd)):
        if G_pd[i][j] == 1:
            for k in range(len(dictionary[nodes_list[i]])):
                if nodes_list[j] in dictionary[nodes_list[i]][k].keys():
                    distance = dictionary[nodes_list[i]][k][nodes_list[j]]
            G_pd[i][j] = distance
        if G_pd[i][j] == 0:
            G_pd[i][j] = 1000000

nodes_numbers = {}
for index, i in enumerate(nodes_list):
    nodes_numbers[i] = index

# вспомогательная функция для подсчета веса дерева и длины кратчайших путей
def tree_weight(tree, matrix):
    end_points = []
    weight = 0
    paths_len = 0
    for i in tree:
        for j in range(len(i) - 1):
            if i[j + 1] not in end_points:
                end_points.append(i[j + 1])
                weight += matrix[nodes_numbers[str(i[j])]][nodes_numbers[str(i[j + 1])]]
            paths_len += matrix[nodes_numbers[str(i[j])]][nodes_numbers[str(i[j + 1])]]

    return weight, paths_len


def short_path_tree():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    hosp_c = list(coordinates['hosp'].values())[0]
    aparts_c = list(coordinates['apart'].values())

    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    routes = []
    route_nodes = []

    for i in aparts_c:
        nearest_node = ox.get_nearest_node(G, (i[0], i[1]))
        route = nx.shortest_path(G,
                                 nearest_node_hosp,
                                 nearest_node,
                                 weight='length')
        node_coordinates = []
        route_nodes.append(route)
        for node in route:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        routes.append(node_coordinates)

    tree_len, paths_len = tree_weight(route_nodes, G_pd)
    return routes, tree_len, paths_len

r, t, p = short_path_tree() # вот так в r записываются пути, в t - вес дерева, в p - длина путей

# эту функцию вызывать когда пользователь нажимает на кластеризацию
def matrix_for_cluster():
    aparts_routes = {}
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    short_path_matrix = np.zeros((len(aparts_c), len(aparts_c)))
    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    for i in range(len(aparts_c)):
        nearest_node1 = ox.get_nearest_node(G, (aparts_c[i][0], aparts_c[i][1]))
        for j in range(len(aparts_c)):
            if aparts_c[i] != aparts_c[j]:
                r = {}
                nearest_node2 = ox.get_nearest_node(G, (aparts_c[j][0], aparts_c[j][1]))
                route = nx.shortest_path(G,
                                         nearest_node1,
                                         nearest_node2,
                                         weight='length')
                r[nearest_node2] = route
                paths_len = 0
                for temp in range(len(route) - 1):
                    paths_len += G_pd[nodes_numbers[str(route[temp])]][nodes_numbers[str(route[temp + 1])]]
                short_path_matrix[i][j] = paths_len
        aparts_routes[nearest_node1] = r

    matrix_cluster = []
    for i in range(len(short_path_matrix)):
        for j in range(i + 1, len(short_path_matrix)):
            if short_path_matrix[i][j] < short_path_matrix[j][i]:
                matrix_cluster.append(short_path_matrix[i][j])
            else:
                matrix_cluster.append(short_path_matrix[j][i])

    m = {}
    m[0] = matrix_cluster

    with open('matrix_cluster.json', 'w') as f:
        json.dump(m, f)

# а это уже при выборе на сколько кластеров

# если 2 кластера
def cluster2():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    with open('matrix_cluster.json') as f:
        matrix_cluster = json.load(f)
    matrix_cluster = list(matrix_cluster.values())[0]

    Z = linkage(matrix_cluster, 'complete')
    num_clust = 2
    Z2 = fcluster(Z, num_clust, 'maxclust')

    c1 = [0, 0]
    c2 = [0, 0]
    k1 = 0
    k2 = 0

    # складываем соответствующие географические координаты узлов в соответствуюшие списки
    for i in range(len(Z2)):
        key = numbers[i]
        coords = coordinates['apart'][key]
        if Z2[i] == 1:
            c1[0] += coords[0]
            c1[1] += coords[1]
            # и считаем количество узлов в кластере для нахождения средних координат
            k1 += 1
        if Z2[i] == 2:
            c2[0] += coords[0]
            c2[1] += coords[1]
            k2 += 1
    # находим среднее значение координат узлов, т. е., координаты наших центроидов
    for i in range(len(c1)):
        c1[i] /= k1
    for j in range(len(c2)):
        c2[j] /= k2
    # ищем ближайшие узлы для наших центроидов
    center1 = ox.get_nearest_node(G, (c1[0], c1[1]))
    center2 = ox.get_nearest_node(G, (c2[0], c2[1]))

    # Находим кратчайшие пути от объекта до центроидов
    hosp_c = list(coordinates['hosp'].values())[0]
    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    path1 = nx.shortest_path(G, nearest_node_hosp, center1, weight='length')
    path2 = nx.shortest_path(G, nearest_node_hosp, center2, weight='length')
    # считаем сумму этих путей
    paths_len = 0
    tree_weight = 0
    end_points = []
    for temp in range(len(path1) - 1):
        tree_weight += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]
        end_points.append(path1[temp])
        paths_len += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]

    for temp in range(len(path2) - 1):
        if path2[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]
            end_points.append(path2[temp])
        paths_len += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]

    short_paths_c1 = {}
    short_paths_c2 = {}

    short_paths_len_c1 = 0
    short_tree_len_c1 = 0

    short_paths_len_c2 = 0
    short_tree_len_c2 = 0

    end_points = []
    for i in range(len(Z2)):
        temp_number = int(numbers[i])
        print(temp_number)
    for i in range(len(Z2)):
        if Z2[i] == 1:
            temp_number = int(numbers[i])
            try:
                path_c1 = nx.shortest_path(G, center1, temp_number, weight='length')
                short_paths_c1[temp_number] = path_c1

                for temp in range(len(path_c1) - 1):
                    if path_c1[temp] not in end_points:
                        short_tree_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
                        end_points.append(path_c1[temp])
                    short_paths_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        else:
            temp_number = int(numbers[i])
            try:
                path_c2 = nx.shortest_path(G, center2, temp_number, weight='length')
                short_paths_c2[temp_number] = path_c2

                for temp in range(len(path_c2) - 1):
                    if path_c2[temp] not in end_points:
                        short_tree_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
                        end_points.append(path_c2[temp])
                    short_paths_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
            except nx.NetworkXNoPath:
                pass

    # длина дерева кратчайших путей от объекта до узлов кластера
    tree_sum1 = tree_weight + short_tree_len_c1 + short_tree_len_c2
    # сумма длин кратчайших путей
    paths_sum1 = paths_len + short_paths_len_c1 + short_paths_len_c2

    print(tree_sum1, paths_sum1)

    # сохраняю координаты всех путей
    # сначала от больницы до центроид
    node_coordinates = []
    routes_from_hosp = []

    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path1:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c1[0], c1[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c1 = []
    # теперь от центроид до узлов
    for i in short_paths_c1.keys():
        node_coordinates = []
        node_coordinates.append([c1[0], c1[1]])
        r_value = short_paths_c1[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c1.append(node_coordinates)

    node_coordinates = []
    node_coordinates.append([hosp_c[0], hosp_c[1]])
    for node in path2:
        temp = []
        temp.append(G.nodes[node]['y'])
        temp.append(G.nodes[node]['x'])
        node_coordinates.append(temp)
    node_coordinates.append([c2[0], c2[1]])
    routes_from_hosp.append(node_coordinates)

    routes_c2 = []
    # теперь от центроид до узлов
    for i in short_paths_c2.keys():
        node_coordinates = []
        node_coordinates.append([c2[0], c2[1]])
        r_value = short_paths_c2[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c2.append(node_coordinates)

    all_routes = []
    all_routes.append(routes_from_hosp)
    all_routes.append(routes_c1)
    all_routes.append(routes_c2)

    return [hosp_c[0], hosp_c[1]], [[c1[0], c1[1]], [c2[0], c2[1]]], all_routes, tree_sum1, paths_sum1

# если 3 кластера
def cluster3():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    with open('matrix_cluster.json') as f:
        matrix_cluster = json.load(f)
    matrix_cluster = list(matrix_cluster.values())[0]

    Z = linkage(matrix_cluster, 'complete')
    num_clust = 3
    Z2 = fcluster(Z, num_clust, 'maxclust')

    c1 = [0, 0]
    c2 = [0, 0]
    c3 = [0, 0]
    k1 = 0
    k2 = 0
    k3 = 0

    # складываем соответствующие географические координаты узлов в соответствуюшие списки
    for i in range(len(Z2)):
        key = numbers[i]
        coords = coordinates['apart'][key]
        if Z2[i] == 1:
            c1[0] += coords[0]
            c1[1] += coords[1]
            # и считаем количество узлов в кластере для нахождения средних координат
            k1 += 1
        if Z2[i] == 2:
            c2[0] += coords[0]
            c2[1] += coords[1]
            k2 += 1
        if Z2[i] == 3:
            c3[0] += coords[0]
            c3[1] += coords[1]
            k3 += 1
    # находим среднее значение координат узлов, т. е., координаты наших центроидов
    for i in range(len(c1)):
        c1[i] /= k1
    for j in range(len(c2)):
        c2[j] /= k2
    for g in range(len(c3)):
        c3[g] /= k3
    # ищем ближайшие узлы для наших центроидов
    center1 = ox.get_nearest_node(G, (c1[0], c1[1]))
    center2 = ox.get_nearest_node(G, (c2[0], c2[1]))
    center3 = ox.get_nearest_node(G, (c3[0], c3[1]))

    # Находим кратчайшие пути от объекта до центроидов
    hosp_c = list(coordinates['hosp'].values())[0]
    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    path1 = nx.shortest_path(G, nearest_node_hosp, center1, weight='length')
    path2 = nx.shortest_path(G, nearest_node_hosp, center2, weight='length')
    path3 = nx.shortest_path(G, nearest_node_hosp, center3, weight='length')
    # считаем сумму этих путей
    paths_len = 0
    tree_weight = 0
    end_points = []
    for temp in range(len(path1) - 1):
        tree_weight += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]
        end_points.append(path1[temp])
        paths_len += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]

    for temp in range(len(path2) - 1):
        if path2[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]
            end_points.append(path2[temp])
        paths_len += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]

    for temp in range(len(path3) - 1):
        if path3[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]
            end_points.append(path3[temp])
        paths_len += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]

    short_paths_c1 = {}
    short_paths_c2 = {}
    short_paths_c3 = {}

    short_paths_len_c1 = 0
    short_tree_len_c1 = 0

    short_paths_len_c2 = 0
    short_tree_len_c2 = 0

    short_paths_len_c3 = 0
    short_tree_len_c3 = 0

    end_points = []
    for i in range(len(Z2)):
        if Z2[i] == 1:
            temp_number = int(numbers[i])
            try:
                path_c1 = nx.shortest_path(G, center1, temp_number, weight='length')
                short_paths_c1[temp_number] = path_c1

                for temp in range(len(path_c1) - 1):
                    if path_c1[temp] not in end_points:
                        short_tree_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
                        end_points.append(path_c1[temp])
                    short_paths_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 2:
            temp_number = int(numbers[i])
            try:
                path_c2 = nx.shortest_path(G, center2, temp_number, weight='length')
                short_paths_c2[temp_number] = path_c2

                for temp in range(len(path_c2) - 1):
                    if path_c2[temp] not in end_points:
                        short_tree_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
                        end_points.append(path_c2[temp])
                    short_paths_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        else:
            temp_number = int(numbers[i])
            try:
                path_c3 = nx.shortest_path(G, center3, temp_number, weight='length')
                short_paths_c3[temp_number] = path_c3

                for temp in range(len(path_c3) - 1):
                    if path_c3[temp] not in end_points:
                        short_tree_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
                        end_points.append(path_c3[temp])
                    short_paths_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
            except nx.NetworkXNoPath:
                pass

    # длина дерева кратчайших путей от объекта до узлов кластера
    tree_sum1 = tree_weight + short_tree_len_c1 + short_tree_len_c2 + short_tree_len_c3
    # сумма длин кратчайших путей
    paths_sum1 = paths_len + short_paths_len_c1 + short_paths_len_c2 + short_paths_len_c3

    # сохраняю координаты всех путей
    # сначала от больницы до центроид

    routes_c1 = []
    # теперь от центроид до узлов
    for i in short_paths_c1.keys():
        node_coordinates = []
        node_coordinates.append([c1[0], c1[1]])
        r_value = short_paths_c1[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c1.append(node_coordinates)

    routes_c2 = []
    # теперь от центроид до узлов
    for i in short_paths_c2.keys():
        node_coordinates = []
        node_coordinates.append([c2[0], c2[1]])
        r_value = short_paths_c2[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c2.append(node_coordinates)

    routes_c3 = []
    # теперь от центроид до узлов
    for i in short_paths_c3.keys():
        node_coordinates = []
        node_coordinates.append([c3[0], c3[1]])
        r_value = short_paths_c3[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c3.append(node_coordinates)

    all_routes = []
    r = []
    all_routes.append(r)
    all_routes.append(routes_c1)
    all_routes.append(routes_c2)
    all_routes.append(routes_c3)

    return [hosp_c[0], hosp_c[1]], [[c1[0], c1[1]], [c2[0], c2[1]], [c3[0], c3[1]]], all_routes, tree_sum1, paths_sum1

# если 5 кластеров
def cluster5():
    with open('coordinates.json') as f:
        coordinates = json.load(f)

    aparts_c = list(coordinates['apart'].values())
    aparts_numbers = list(coordinates['apart'].keys())

    numbers = {}
    k = 0
    for n in aparts_numbers:
        numbers[k] = n
        k += 1

    print(numbers)

    with open('matrix_cluster.json') as f:
        matrix_cluster = json.load(f)
    matrix_cluster = list(matrix_cluster.values())[0]

    Z = linkage(matrix_cluster, 'complete')
    num_clust = 5
    Z2 = fcluster(Z, num_clust, 'maxclust')

    c1 = [0, 0]
    c2 = [0, 0]
    c3 = [0, 0]
    c4 = [0, 0]
    c5 = [0, 0]
    k1 = 0
    k2 = 0
    k3 = 0
    k4 = 0
    k5 = 0

    # складываем соответствующие географические координаты узлов в соответствуюшие списки
    for i in range(len(Z2)):
        key = numbers[i]
        coords = coordinates['apart'][key]
        if Z2[i] == 1:
            c1[0] += coords[0]
            c1[1] += coords[1]
            # и считаем количество узлов в кластере для нахождения средних координат
            k1 += 1
        if Z2[i] == 2:
            c2[0] += coords[0]
            c2[1] += coords[1]
            k2 += 1
        if Z2[i] == 3:
            c3[0] += coords[0]
            c3[1] += coords[1]
            k3 += 1
        if Z2[i] == 4:
            c4[0] += coords[0]
            c4[1] += coords[1]
            k4 += 1
        if Z2[i] == 5:
            c5[0] += coords[0]
            c5[1] += coords[1]
            k5 += 1
    # находим среднее значение координат узлов, т. е., координаты наших центроидов
    for i in range(len(c1)):
        c1[i] /= k1
    for j in range(len(c2)):
        c2[j] /= k2
    for g in range(len(c3)):
        c3[g] /= k3
    for i in range(len(c4)):
        c4[i] /= k4
    for j in range(len(c5)):
        c5[j] /= k5
    # ищем ближайшие узлы для наших центроидов
    center1 = ox.get_nearest_node(G, (c1[0], c1[1]))
    center2 = ox.get_nearest_node(G, (c2[0], c2[1]))
    center3 = ox.get_nearest_node(G, (c3[0], c3[1]))
    center4 = ox.get_nearest_node(G, (c4[0], c4[1]))
    center5 = ox.get_nearest_node(G, (c5[0], c5[1]))

    # Находим кратчайшие пути от объекта до центроидов
    hosp_c = list(coordinates['hosp'].values())[0]
    nearest_node_hosp = ox.get_nearest_node(G, (hosp_c[0], hosp_c[1]))
    path1 = nx.shortest_path(G, nearest_node_hosp, center1, weight='length')
    path2 = nx.shortest_path(G, nearest_node_hosp, center2, weight='length')
    path3 = nx.shortest_path(G, nearest_node_hosp, center3, weight='length')
    path4 = nx.shortest_path(G, nearest_node_hosp, center4, weight='length')
    path5 = nx.shortest_path(G, nearest_node_hosp, center5, weight='length')
    # считаем сумму этих путей
    paths_len = 0
    tree_weight = 0
    end_points = []
    for temp in range(len(path1) - 1):
        tree_weight += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]
        end_points.append(path1[temp])
        paths_len += G_pd[nodes_numbers[str(path1[temp])]][nodes_numbers[str(path1[temp + 1])]]

    for temp in range(len(path2) - 1):
        if path2[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]
            end_points.append(path2[temp])
        paths_len += G_pd[nodes_numbers[str(path2[temp])]][nodes_numbers[str(path2[temp + 1])]]

    for temp in range(len(path3) - 1):
        if path3[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]
            end_points.append(path3[temp])
        paths_len += G_pd[nodes_numbers[str(path3[temp])]][nodes_numbers[str(path3[temp + 1])]]

    for temp in range(len(path4) - 1):
        if path4[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path4[temp])]][nodes_numbers[str(path4[temp + 1])]]
            end_points.append(path4[temp])
        paths_len += G_pd[nodes_numbers[str(path4[temp])]][nodes_numbers[str(path4[temp + 1])]]

    for temp in range(len(path5) - 1):
        if path5[temp] not in end_points:
            tree_weight += G_pd[nodes_numbers[str(path5[temp])]][nodes_numbers[str(path5[temp + 1])]]
            end_points.append(path5[temp])
        paths_len += G_pd[nodes_numbers[str(path5[temp])]][nodes_numbers[str(path5[temp + 1])]]

    short_paths_c1 = {}
    short_paths_c2 = {}
    short_paths_c3 = {}
    short_paths_c4 = {}
    short_paths_c5 = {}

    short_paths_len_c1 = 0
    short_tree_len_c1 = 0

    short_paths_len_c2 = 0
    short_tree_len_c2 = 0

    short_paths_len_c3 = 0
    short_tree_len_c3 = 0

    short_paths_len_c4 = 0
    short_tree_len_c4 = 0

    short_paths_len_c5 = 0
    short_tree_len_c5 = 0

    end_points = []
    for i in range(len(Z2)):
        if Z2[i] == 1:
            temp_number = int(numbers[i])
            try:
                path_c1 = nx.shortest_path(G, center1, temp_number, weight='length')
                short_paths_c1[temp_number] = path_c1

                for temp in range(len(path_c1) - 1):
                    if path_c1[temp] not in end_points:
                        short_tree_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
                        end_points.append(path_c1[temp])
                    short_paths_len_c1 += G_pd[nodes_numbers[str(path_c1[temp])]][nodes_numbers[str(path_c1[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 2:
            temp_number = int(numbers[i])
            try:
                path_c2 = nx.shortest_path(G, center2, temp_number, weight='length')
                short_paths_c2[temp_number] = path_c2

                for temp in range(len(path_c2) - 1):
                    if path_c2[temp] not in end_points:
                        short_tree_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
                        end_points.append(path_c2[temp])
                    short_paths_len_c2 += G_pd[nodes_numbers[str(path_c2[temp])]][nodes_numbers[str(path_c2[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 3:
            temp_number = int(numbers[i])
            try:
                path_c3 = nx.shortest_path(G, center3, temp_number, weight='length')
                short_paths_c3[temp_number] = path_c3

                for temp in range(len(path_c3) - 1):
                    if path_c3[temp] not in end_points:
                        short_tree_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
                        end_points.append(path_c3[temp])
                    short_paths_len_c3 += G_pd[nodes_numbers[str(path_c3[temp])]][nodes_numbers[str(path_c3[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        if Z2[i] == 4:
            temp_number = int(numbers[i])
            try:
                path_c4 = nx.shortest_path(G, center4, temp_number, weight='length')
                short_paths_c4[temp_number] = path_c4

                for temp in range(len(path_c4) - 1):
                    if path_c4[temp] not in end_points:
                        short_tree_len_c4 += G_pd[nodes_numbers[str(path_c4[temp])]][nodes_numbers[str(path_c4[temp + 1])]]
                        end_points.append(path_c4[temp])
                    short_paths_len_c4 += G_pd[nodes_numbers[str(path_c4[temp])]][nodes_numbers[str(path_c4[temp + 1])]]
            except nx.NetworkXNoPath:
                pass
        else:
            temp_number = int(numbers[i])
            try:
                path_c5 = nx.shortest_path(G, center5, temp_number, weight='length')
                short_paths_c5[temp_number] = path_c5

                for temp in range(len(path_c5) - 1):
                    if path_c5[temp] not in end_points:
                        short_tree_len_c5 += G_pd[nodes_numbers[str(path_c5[temp])]][nodes_numbers[str(path_c5[temp + 1])]]
                        end_points.append(path_c5[temp])
                    short_paths_len_c5 += G_pd[nodes_numbers[str(path_c5[temp])]][nodes_numbers[str(path_c5[temp + 1])]]
            except nx.NetworkXNoPath:
                pass

    # длина дерева кратчайших путей от объекта до узлов кластера
    tree_sum1 = tree_weight + short_tree_len_c1 + short_tree_len_c2 + short_tree_len_c3 + short_tree_len_c4 + short_tree_len_c5
    # сумма длин кратчайших путей
    paths_sum1 = paths_len + short_paths_len_c1 + short_paths_len_c2 + short_paths_len_c3 + short_paths_len_c4 + short_paths_len_c5

    # сохраняю координаты всех путей
    # сначала от больницы до центроид

    routes_c1 = []
    # теперь от центроид до узлов
    for i in short_paths_c1.keys():
        node_coordinates = []
        node_coordinates.append([c1[0], c1[1]])
        r_value = short_paths_c1[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c1.append(node_coordinates)


    routes_c2 = []
    # теперь от центроид до узлов
    for i in short_paths_c2.keys():
        node_coordinates = []
        node_coordinates.append([c2[0], c2[1]])
        r_value = short_paths_c2[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c2.append(node_coordinates)

    routes_c3 = []
    # теперь от центроид до узлов
    for i in short_paths_c3.keys():
        node_coordinates = []
        node_coordinates.append([c3[0], c3[1]])
        r_value = short_paths_c3[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c3.append(node_coordinates)

    routes_c4 = []
    # теперь от центроид до узлов
    for i in short_paths_c4.keys():
        node_coordinates = []
        node_coordinates.append([c4[0], c4[1]])
        r_value = short_paths_c4[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c4.append(node_coordinates)

    routes_c5 = []
    # теперь от центроид до узлов
    for i in short_paths_c5.keys():
        node_coordinates = []
        node_coordinates.append([c5[0], c5[1]])
        r_value = short_paths_c5[i]

        for node in r_value:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(i)])
        routes_c5.append(node_coordinates)

    all_routes = []
    r = []
    all_routes.append(r)
    all_routes.append(routes_c1)
    all_routes.append(routes_c2)
    all_routes.append(routes_c3)
    all_routes.append(routes_c4)
    all_routes.append(routes_c5)

    return [hosp_c[0], hosp_c[1]], [[c1[0], c1[1]], [c2[0], c2[1]], [c3[0], c3[1]], [c4[0], c4[1]],
                                    [c5[0], c5[1]]], all_routes, tree_sum1, paths_sum1



