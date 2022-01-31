import random
import pickle
import sys
import copy

class temp_map:
    def __init__(self, vne_list, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        for i in vne_list:
            self.node_cost += sum(i.node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = dict()


class Graph:
    def __init__(self, nodes, edges, edge_weights, node_weights) -> None:
        self.nodes = nodes
        self.edges = edges
        self.neighbours = dict()
        self.node_weights = node_weights
        self.edge_weights = edge_weights
        for i in range(self.nodes):
            self.neighbours[i] = set()
            for a, b in self.edges:
                if int(a) == i:
                    self.neighbours[i].add(b)

    def findPaths(self, s, d, visited, path, all_paths, weight):
        visited[int(s)] = True
        path.append(s)
        if s == d:
            all_paths.append(path.copy())
        else:
            for i in self.neighbours[int(s)]:
                if visited[int(i)] == False and self.edge_weights[(s, i)] >= weight:
                    self.findPaths(i, d, visited, path, all_paths, weight)

        path.pop()
        visited[int(s)] = False

    def findPathFromSrcToDst(self, s, d, weight):

        all_paths = []
        visited = [False] * (self.nodes)
        path = []
        self.findPaths(s, d, visited, path, all_paths, weight)
        if all_paths == []:
            return []
        else:
            return all_paths[random.randint(0, len(all_paths) - 1)]

    def BFS(self, src, dest, v, pred, dist, weight):
        queue = []
        visited = [False for i in range(v)]
        for i in range(v):
            dist[i] = 1000000
            pred[i] = -1
        visited[int(src)] = True
        dist[int(src)] = 0
        queue.append(src)
        while len(queue) != 0:
            u = queue[0]
            queue.pop(0)
            for i in self.neighbours[int(u)]:
                if visited[int(i)] == False and self.edge_weights[(u, i)] >= weight:
                    visited[int(i)] = True
                    dist[int(i)] = dist[int(u)] + 1
                    pred[int(i)] = u
                    queue.append(i)
                    if i == dest:
                        return True

        return False

    def findShortestPath(self, s, dest, weight):
        v = self.nodes
        pred = [0 for i in range(v)]
        dist = [0 for i in range(v)]
        ls = []
        if self.BFS(s, dest, v, pred, dist, weight) == False:
            return ls
        path = []
        crawl = dest
        crawl = dest
        path.append(crawl)

        while pred[int(crawl)] != -1:
            path.append(pred[int(crawl)])
            crawl = pred[int(crawl)]

        for i in range(len(path) - 1, -1, -1):
            ls.append(path[i])

        return ls


def tester():
    nodes = 8
    edges = [
        ("0", "1"),
        ("1", "0"),
        ("0", "3"),
        ("3", "0"),
        ("0", "4"),
        ("4", "0"),
        ("3", "4"),
        ("4", "3"),
        ("1", "2"),
        ("2", "1"),
        ("2", "4"),
        ("4", "2")
    ]
    edge_weights = {
        ("0", "1"):8,
        ("1", "0"):8,
        ("0", "3"):6,
        ("3", "0"):6,
        ("0", "4"):10,
        ("4", "0"):10,
        ("3", "4"):6,
        ("4", "3"):6,
        ("1", "2"):6,
        ("2", "1"):6,
        ("2", "4"):6,
        ("4", "2"):6
    }
    node_weights = {
        0:10,
        1:10,
        2:10,
        3:10,
        4:10,
        5:10,
        6:10,
        7:10
    }
    substrate = Graph(nodes, edges, edge_weights, node_weights)
    vne_list = []


    nodes = 2
    edges = [("0", "1"), ("1", "0")]
    edge_weights = dict()
    node_weights = dict()
    edge_weights[("0", "1")] = 5
    edge_weights["1", "0"] = 5
    node_weights[0] = 9
    node_weights[1] = 8
    vne_list.append(Graph(nodes, edges, edge_weights, node_weights))

    output = {
            "substrate": substrate,
            "vne_list": vne_list
        }
    pickle_file = open("static.pickle", "wb")
    pickle.dump(output, pickle_file)

if __name__ == "__main__":
    tester()
