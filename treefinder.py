# Only for simulation

import latlng

class Tree:
    def __init__(self, category, lat, lng):
        self.category = category
        self.lat = lat
        self.lng = lng

class TreeFinder:

    def __init__(self, filename, grid_size = 5):
        self.tree_finder = []
        self.trees = []
        self.count = 0
        self.max_lat = -1e99
        self.min_lat = 1e99
        self.max_lng = -1e99
        self.min_lng = 1e99
        self.grid_size = grid_size
        for line in open(filename,'r'):
            temp = line.split(';')
            tree = Tree(temp[0],float(temp[1]),float(temp[2]))
            self.trees.append(tree)
            self.max_lat = max(self.max_lat, tree.lat)
            self.min_lat = min(self.min_lat, tree.lat)
            self.max_lng = max(self.max_lng, tree.lng)
            self.min_lng = min(self.min_lng, tree.lng)
        w = latlng.LatLng(self.min_lat, self.min_lng).get_xy(latlng.LatLng(self.min_lat, self.max_lng)).x
        h = latlng.LatLng(self.min_lat, self.min_lng).get_xy(latlng.LatLng(self.max_lat, self.min_lng)).y
        self.n_lat = int(h / grid_size) + 1
        self.n_lng = int(w / grid_size) + 1
        self.k_lat = int((self.n_lat-1)/(self.max_lat-self.min_lat))
        self.k_lng = int((self.n_lng-1)/(self.max_lng-self.min_lng))
        for i in range(self.n_lat):
            self.tree_finder.append([])
            for j in range(self.n_lng):
                self.tree_finder[i].append([])
        for tree in self.trees:
            self.add_tree(tree)

    def add_tree(self, tree):
        i = int((tree.lat - self.min_lat) * self.k_lat)
        j = int((tree.lng - self.min_lng) * self.k_lng)
        self.tree_finder[i][j].append(tree)
        self.count += 1

    def find_trees(self, lat, lng, radius = 5):
        trees = []
        grid_range = int(radius/self.grid_size) + 1
        i = int((lat - self.min_lat) * self.k_lat)
        j = int((lng - self.min_lng) * self.k_lng)
        for p in range(i-grid_range,i+grid_range+1):
            for q in range(j-grid_range,j+grid_range+1):
                if 0 <= p and p < self.n_lat and 0<=q and q < self.n_lng:
                    for tree in self.tree_finder[p][q]:
                        if latlng.LatLng(lat,lng).get_distance(latlng.LatLng(tree.lat,tree.lng)) < radius:
                            trees.append(tree)
        return trees

    def find_nearest_trees(self, lat, lng, radius = 5):
        grid_range = int(radius/self.grid_size) + 1
        i = int((lat - self.min_lat) * self.k_lat)
        j = int((lng - self.min_lng) * self.k_lng)
        m_dis = 1e99
        m_tree = None
        for p in range(i-grid_range,i+grid_range+1):
            for q in range(j-grid_range,j+grid_range+1):
                if 0 <= p and p < self.n_lat and 0<=q and q < self.n_lng:
                    for tree in self.tree_finder[p][q]:
                        dis = latlng.LatLng(lat,lng).get_distance(latlng.LatLng(tree.lat,tree.lng))
                        if dis < m_dis:
                            m_dis = dis
                            m_tree = tree
        return m_tree

    def calc_performance(self, roadnetwork):
        TP_a = 0
        TN_a = 0
        recall_a = 0
        precision_a = 0
        accuracy_a = 0
        TP_p = 0
        TN_p = 0
        recall_p = 0
        precision_p = 0
        accuracy_p = 0
        for road in roadnetwork.roads:
            for aggregated_tree in road.aggregator.aggregated_objects:
                nt = self.find_nearest_trees(aggregated_tree.lat, aggregated_tree.lng)
                if nt is None:
                    TN_a += 1
                    break
                if aggregated_tree.get_distance(latlng.LatLng(nt.lat, nt.lng)) < 5:
                    TP_a += 1
                    accuracy_a += aggregated_tree.get_distance(latlng.LatLng(nt.lat, nt.lng))
                else:
                    TN_a += 1
            for predicted_tree in road.predictor.predicted_objects:
                nt = self.find_nearest_trees(predicted_tree.lat, predicted_tree.lng)
                if nt is None:
                    TN_p += 1
                    break
                if predicted_tree.get_distance(latlng.LatLng(nt.lat, nt.lng)) < 5:
                    TP_p += 1
                    accuracy_p += predicted_tree.get_distance(latlng.LatLng(nt.lat, nt.lng))
                else:
                    TN_p += 1
        if TP_a > 0:
            precision_a = TP_a/(TP_a+TN_a)
            recall_a = TP_a/self.count
            accuracy_a /= TP_a
        if TP_p > 0:
            precision_p = TP_p/(TP_p+TN_p)
            recall_p = TP_p/self.count
            accuracy_p /= TP_p
        return recall_a, precision_a, accuracy_a, recall_p, precision_p, accuracy_p
