def coordinates_and_matrix(N1, N2):
    # N1 - количество больниц
    # N2 - количество домов
    buildings = ox.footprints.footprints_from_place(place, footprint_type='building', retain_invalid=False,
                                                    which_result=1)

    hospitalss = []
    apartmentss = []
    n = 10000
    build = buildings.head(n)['building'].to_dict()

    for key, value in build.items():
        if value == 'hospital':
            hospitalss.append(key)
        elif value == 'apartments':
            apartmentss.append(key)

    # реализация рандомного выбора
    hospitals = []
    i = 0
    while i != N1:
        temp = hospitalss[randint(0, len(hospitalss) - 1)]
        if temp not in hospitals:
            hospitals.append(temp)
            i += 1
    apartments = []
    i = 0
    while i != N2:
        temp = apartmentss[randint(0, len(apartmentss) - 1)]
        if temp not in apartments:
            apartments.append(temp)
            i += 1

    # теперь берем координаты и находим ближайшие узлы

    a = buildings.head(n).to_dict()
    hospitals_dict = {}
    apartments_dict = {}

    coordinates = []
    cord_hosp = []
    cord_aparts = []

    numbers_of_nodes = {'apart': {'id_to_number': {}, 'number_to_id': {}},
                        'hosp': {'id_to_number': {}, 'number_to_id': {}}}
    count = 0

    for i in apartments:
        bounds = a['geometry'][i].bounds
        temp = []
        x = (bounds[1] + bounds[3]) / 2
        y = (bounds[0] + bounds[2]) / 2
        temp.append(x)
        temp.append(y)
        nearest_node = ox.get_nearest_node(G, (x, y))
        apartments_dict[str(nearest_node)] = temp
        cord_aparts.append(temp)
        numbers_of_nodes['apart']['id_to_number'][str(nearest_node)] = count
        numbers_of_nodes['apart']['number_to_id'][count] = str(nearest_node)
        count += 1

    for i in hospitals:
        bounds = a['geometry'][i].bounds
        temp = []
        x = (bounds[1] + bounds[3]) / 2
        y = (bounds[0] + bounds[2]) / 2
        temp.append(x)
        temp.append(y)
        nearest_node = ox.get_nearest_node(G, (x, y))
        hospitals_dict[str(nearest_node)] = temp
        cord_hosp.append(temp)
        numbers_of_nodes['hosp']['id_to_number'][str(nearest_node)] = count
        numbers_of_nodes['hosp']['number_to_id'][count] = str(nearest_node)
        count += 1

    coordinates.append(cord_hosp)
    coordinates.append(cord_aparts)

    dict_for_items = {}
    dict_for_items['hosp'] = hospitals_dict
    dict_for_items['apart'] = apartments_dict

    matrix_of_short_paths = np.zeros((N1 + N2, N1 + N2))

    for i in range(N2):
        for j in range(N2 + N1):
            if j >= N2:
                node2 = int(numbers_of_nodes['hosp']['number_to_id'][j])
            if j < N2:
                node2 = int(numbers_of_nodes['apart']['number_to_id'][j])
            if i != j:
                node1 = int(numbers_of_nodes['apart']['number_to_id'][i])
                dist = nx.shortest_path_length(G, node1, node2, weight='length')
                matrix_of_short_paths[i][j] = dist

    for i in range(N2, N2 + N1):
        for j in range(N2 + N1):
            if j >= N2:
                node2 = int(numbers_of_nodes['hosp']['number_to_id'][j])
            if j < N2:
                node2 = int(numbers_of_nodes['apart']['number_to_id'][j])
            if i != j:
                node1 = int(numbers_of_nodes['hosp']['number_to_id'][i])
                dist = nx.shortest_path_length(G, node1, node2, weight='length')
                matrix_of_short_paths[i][j] = dist

    with open('coordinates_task1.json', 'w') as f:
        json.dump(dict_for_items, f)

    with open('numbers_of_nodes.json', 'w') as f:
        json.dump(numbers_of_nodes, f)

    return coordinates


def find_nearest_hospitals_1a(dist_matrix, apart_count=100):
    nearest_hosp_list = [[-1 for i in range(3)] for j in range(apart_count)]
    for i in range(apart_count):
        nearest_hosp_list[i][0] = np.argmin(dist_matrix[i][apart_count:]) + apart_count
        nearest_hosp_list[i][1] = np.argmin(np.array(dist_matrix[apart_count:]).transpose()[i]) + apart_count
        tuda = dist_matrix[i][apart_count:]
        suda = np.array(dist_matrix[apart_count:]).transpose()[i]
        nearest_hosp_list[i][2] = np.argmin(tuda + suda) + apart_count

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)


    tuda_suda = {'tuda': {}, 'suda': {}, 'tuda_suda': {}}

    for i in range(len(nearest_hosp_list)):
        apart = int(numbers_of_nodes['apart']['number_to_id'][str(i)])
        hosp_tuda = int(numbers_of_nodes['hosp']['number_to_id'][str(nearest_hosp_list[i][0])])
        hosp_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(nearest_hosp_list[i][1])])
        hosp_tuda_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(nearest_hosp_list[i][2])])

        route_tuda = nx.shortest_path(G,
                                      apart,
                                      hosp_tuda,
                                      weight='length')
        route_suda = nx.shortest_path(G,
                                      hosp_suda,
                                      apart,
                                      weight='length')
        temp1 = nx.shortest_path(G,
                                 apart,
                                 hosp_tuda_suda,
                                 weight='length')
        temp2 = nx.shortest_path(G,
                                 hosp_tuda_suda,
                                 apart,
                                 weight='length')
        route_tuda_suda = temp1 + temp2

        node_coordinates = []
        node_coordinates.append(coordinates['apart'][str(apart)])
        for node in route_tuda:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['hosp'][str(hosp_tuda)])
        tuda_suda['tuda'][str(apart)] = node_coordinates

        node_coordinates = []
        node_coordinates.append(coordinates['hosp'][str(hosp_suda)])
        for node in route_suda:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(apart)])
        tuda_suda['suda'][str(apart)] = node_coordinates

        node_coordinates = []
        node_coordinates.append(coordinates['apart'][str(apart)])
        for node in route_tuda_suda:
            temp = []
            temp.append(G.nodes[node]['y'])
            temp.append(G.nodes[node]['x'])
            node_coordinates.append(temp)
        node_coordinates.append(coordinates['apart'][str(apart)])
        tuda_suda['tuda_suda'][str(apart)] = node_coordinates

        with open('tuda_suda.json', 'w') as f:
            json.dump(tuda_suda, f)


def tuda(apart_coords):
    node = ox.get_nearest_node(G, (float(apart_coords[0]), float(apart_coords[0])))

    with open('tuda_suda.json') as f:
        tuda_suda = json.load(f)

    route = tuda_suda['tuda'][str(node)]

    return route


def suda(apart_coords):
    node = ox.get_nearest_node(G, (float(apart_coords[0]), float(apart_coords[0])))

    with open('tuda_suda.json') as f:
        tuda_suda = json.load(f)

    route = tuda_suda['suda'][str(node)]

    return route


def tuda_suda(apart_coords):
    node = ox.get_nearest_node(G, (float(apart_coords[0]), float(apart_coords[0])))

    with open('tuda_suda.json') as f:
        tuda_suda = json.load(f)

    route = tuda_suda['tuda_suda'][str(node)]

    return route


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

    with open('numbers_of_nodes.json') as f:
        numbers_of_nodes = json.load(f)

    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    tuda_suda_radius = {'tuda': {}, 'suda': {}, 'tuda_suda': {}}

    for i in range(len(permissible_hosps)):
        apart = int(numbers_of_nodes['apart']['number_to_id'][str(i)])

        temp_cord = []
        for j in range(len(permissible_hosps[i][0])):
            hosp_tuda = int(numbers_of_nodes['hosp']['number_to_id'][str(permissible_hosps[i][0][j])])
            route_tuda = nx.shortest_path(G,
                                          apart,
                                          hosp_tuda,
                                          weight='length')
            node_coordinates = []
            node_coordinates.append(coordinates['apart'][str(apart)])
            for node in route_tuda:
                temp = []
                temp.append(G.nodes[node]['y'])
                temp.append(G.nodes[node]['x'])
                node_coordinates.append(temp)
            node_coordinates.append(coordinates['hosp'][str(hosp_tuda)])
            temp_cord.append(node_coordinates)
        tuda_suda_radius['tuda'][str(apart)] = temp_cord

        temp_cord = []
        for j in range(len(permissible_hosps[i][1])):
            hosp_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(permissible_hosps[i][1][j])])
            route_suda = nx.shortest_path(G,
                                          hosp_suda,
                                          apart,
                                          weight='length')
            node_coordinates = []
            node_coordinates.append(coordinates['hosp'][str(hosp_suda)])
            for node in route_suda:
                temp = []
                temp.append(G.nodes[node]['y'])
                temp.append(G.nodes[node]['x'])
                node_coordinates.append(temp)
            node_coordinates.append(coordinates['apart'][str(apart)])
            temp_cord.append(node_coordinates)
        tuda_suda_radius['suda'][str(apart)] = temp_cord

        temp_cord = []
        for j in range(len(permissible_hosps[i][2])):
            hosp_tuda_suda = int(numbers_of_nodes['hosp']['number_to_id'][str(permissible_hosps[i][2][j])])
            temp1 = nx.shortest_path(G,
                                     apart,
                                     hosp_tuda_suda,
                                     weight='length')
            temp2 = nx.shortest_path(G,
                                     hosp_tuda_suda,
                                     apart,
                                     weight='length')
            route_tuda_suda = temp1 + temp2

            node_coordinates = []
            node_coordinates.append(coordinates['apart'][str(apart)])
            for node in route_tuda_suda:
                temp = []
                temp.append(G.nodes[node]['y'])
                temp.append(G.nodes[node]['x'])
                node_coordinates.append(temp)
            node_coordinates.append(coordinates['apart'][str(apart)])
            temp_cord.append(node_coordinates)
        tuda_suda_radius['tuda_suda'][str(apart)] = temp_cord

    with open('tuda_suda_radius.json', 'w') as f:
        json.dump(tuda_suda, f)


def tuda_radius(apart_coords):
    node = ox.get_nearest_node(G, (float(apart_coords[0]), float(apart_coords[0])))

    with open('tuda_suda_radius.json') as f:
        tuda_suda = json.load(f)

    routes = tuda_suda['tuda'][str(node)]

    return routes


def suda_radius(apart_coords):
    node = ox.get_nearest_node(G, (float(apart_coords[0]), float(apart_coords[0])))

    with open('tuda_suda_radius.json') as f:
        tuda_suda = json.load(f)

    routes = tuda_suda['suda'][str(node)]

    return routes


def tuda_suda_radius(apart_coords):
    node = ox.get_nearest_node(G, (float(apart_coords[0]), float(apart_coords[0])))

    with open('tuda_suda_radius.json') as f:
        tuda_suda = json.load(f)

    routes = tuda_suda['tuda_suda'][str(node)]

    return routes


