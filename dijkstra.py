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


pred_dict = {}

for i in range(len(A)):
    pred = {}
    distance = dijkstra(len(A), i, A)
    # словарь предшественников следующего вида:
    # у каждого узла-корня есть список его детей,
    # а у каждого ребенка - его предок
    pred_dict[i] = pred

print(pred_dict)
# вывод:
# {0: {1: 0, 5: 0, 2: 4, 4: 5, 3: 4},
# 1: {2: 1, 4: 1, 3: 4, 0: 3, 5: 3},
# 2: {3: 2, 0: 3, 5: 3, 1: 5, 4: 5},
# 3: {0: 3, 5: 3, 1: 5, 4: 5, 2: 4},
# 4: {2: 4, 3: 4, 0: 3, 5: 3, 1: 5},
# 5: {1: 5, 4: 5, 2: 4, 3: 4, 0: 3}}

def find_short_path(pred_dict, index_a, index_b):
    path = []
    path.append(index_b)
    temp = index_b
    while pred_dict[index_a][temp] != index_a:
        path.append(pred_dict[index_a][temp])
        temp = pred_dict[index_a][temp]
    path.append(index_a)
    path.reverse()
    return path

path = find_short_path(pred_dict, 0, 1)
print(path)
# вывод
# [0, 1]

def short_path_value(path, matrix):
    value = 0
    for i in range(len(path)-1):
        value += matrix[path[i]][path[i+1]]
    return value

value = short_path_value(path, A)

# запись в json потому что в csv я не знаю как и зачем, он же для таблиц
import json
with open('try_tree.json', 'w') as f:
    json.dump(pred_dict, f)

with open('try_tree.json') as f:
    short_path_tree = json.load(f)
print(short_path_tree)

def find_all_short_path(pred_dict):
    short_paths = {}
    for i in pred_dict.keys():
        path = {}
        for j in pred_dict[i].keys():
            path[j] = find_short_path(pred_dict, i, j)
        short_paths[i] = path
    return short_paths

short_paths = find_all_short_path(pred_dict)

# запись
# with open('short_paths.json', 'w') as f:
#     json.dump(short_paths, f)
#
# with open('short_paths.json') as f:
#     short_paths = json.load(f)
#print(short_paths)

def tree_weight(tree, root, matrix):
    weight = 0
    for i in tree[root].keys():
        j = tree[root][i]
        weight += matrix[j][int(i)]
    return weight

w = tree_weight(pred_dict, 0, A)
print(w)

def minimal_tree(tree, matrix):
    min_value = 10000000000
    root = 0
    for i in tree.keys():
        temp = tree_weight(tree, i, matrix)
        if temp < min_value:
            min_value = temp
            root = i
    return root

k = minimal_tree(short_path_tree, A)
print(k)

def minimal_tree_hospitals(tree, matrix, hospitals):
    min_value = 10000000000
    root = 0
    for i in hospitals:
        temp = tree_weight(tree, str(i), matrix)
        print(i, temp)
        if temp < min_value:
            min_value = temp
            root = i
    return root

hospitals = [1, 2, 3]

k = minimal_tree_hospitals(short_path_tree, A, hospitals)
print(k)





