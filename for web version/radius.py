import math

# для того, чтобы найти объекты в радиусе, нужна функция для подсчета расстояния между географическими координатами

def distance(geo_cor1, geo_cor2):
    rad = 6372795

    # координаты двух точек
    llat1 = geo_cor1[0]
    llong1 = geo_cor1[1]

    llat2 = geo_cor2[0]
    llong2 = geo_cor2[1]

    # в радианах
    lat1 = llat1 * math.pi / 180.
    lat2 = llat2 * math.pi / 180.
    long1 = llong1 * math.pi / 180.
    long2 = llong2 * math.pi / 180.

    # косинусы и синусы широт и разницы долгот
    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    # вычисления длины большого круга
    y = math.sqrt(math.pow(cl2 * sdelta, 2) + math.pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta
    ad = math.atan2(y, x)
    dist = ad * rad

    return dist


# Эта функция должна вызываться при нажатии на кнопку: Найти ближайшие объекты в радиусе
# Ничего не возвращает
def find_the_distance():
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    aparts = coordinates['apart']

    hosps = coordinates['hosp']

    distance_dict = {}

    for i in aparts.keys():
        coord1 = aparts[i]
        temp = {}
        for j in hosps.keys():
            coord2 = hosps[j]
            dist = distance(coord1, coord2)
            temp[dist] = [coord1, coord2]
        distance_dict[i] = temp

    with open('radius.json', 'w') as f:
        json.dump(distance_dict, f)

# эту функцию вызывать, когда пользователь написал радиус и ! выбрал дом !
# будет возвращаться список путей из дома до больниц, а точнее просто координаты двух узлов
def nodes_in_radius(rad, apart_coords):
    with open('coordinates_task1.json') as f:
        coordinates = json.load(f)

    node = ""
    for c in coordinates['apart'].keys():
        if coordinates['apart'][c][0] == apart_coords[0] and coordinates['apart'][c][1] == apart_coords[1]:
            node = c

    with open('radius.json') as f:
        radius = json.load(f)

    list_of_routes = []
    for i in radius[node].keys():
        if float(i) <= rad:
            list_of_routes.append(radius[node][i])
    return list_of_routes