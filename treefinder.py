# Only for simulation

import latlng

class Tree:
    def __init__(self, id, category, lat, lng):
        self.category = category
        self.lat = lat
        self.lng = lng
        self.id = id

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
        tid = 0
        for line in open(filename,'r'):
            temp = line.split(';')
            tree = Tree(tid, temp[0],float(temp[1]),float(temp[2]))
            tid += 1
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
        self.tree_vis = [False for tree in self.trees]
        for tree in self.trees:
            self.add_tree(tree)

    def add_tree(self, tree):
        i = int((tree.lat - self.min_lat) * self.k_lat)
        j = int((tree.lng - self.min_lng) * self.k_lng)
        self.tree_finder[i][j].append(tree)
        self.count += 1

    def find_trees(self, lat, lng, radius = 5):
        trees = []
        grid_range = int((radius-0.1)/self.grid_size) + 1
        i = int((lat - self.min_lat) * self.k_lat)
        j = int((lng - self.min_lng) * self.k_lng)
        for p in range(i-grid_range,i+grid_range+1):
            for q in range(j-grid_range,j+grid_range+1):
                if 0 <= p and p < self.n_lat and 0<=q and q < self.n_lng:
                    for tree in self.tree_finder[p][q]:
                        if latlng.LatLng(lat,lng).get_distance(latlng.LatLng(tree.lat,tree.lng)) < radius:
                            trees.append(tree)
        return trees

    def find_the_nearest_tree(self, lat, lng, radius = 5):
        grid_range = int((radius-0.1)/self.grid_size) + 1
        i = int((lat - self.min_lat) * self.k_lat)
        j = int((lng - self.min_lng) * self.k_lng)
        m_dis = 1e99
        m_tree = None
        for p in range(i-grid_range,i+grid_range+1):
            for q in range(j-grid_range,j+grid_range+1):
                if 0 <= p and p < self.n_lat and 0<=q and q < self.n_lng:
                    for tree in self.tree_finder[p][q]:
                        if self.tree_vis[tree.id] == False:
                            dis = latlng.LatLng(lat,lng).get_distance(latlng.LatLng(tree.lat,tree.lng))
                            if dis < m_dis and dis < radius:
                                m_dis = dis
                                m_tree = tree
        return m_tree

    def calc_performance(self, roadnetwork, filename = ""):
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
        self.tree_vis = [False for tree in self.trees]
        for road in roadnetwork.roads:
            for aggregated_tree in road.aggregator.aggregated_objects:
                nt = self.find_the_nearest_tree(aggregated_tree.lat, aggregated_tree.lng, 3)
                if nt is None:
                    TN_a += 1
                    break
                TP_a += 1
                self.tree_vis[nt.id] = True
                accuracy_a += aggregated_tree.get_distance(latlng.LatLng(nt.lat, nt.lng))

            for predicted_tree in road.predictor.predicted_objects:
                nt = self.find_the_nearest_tree(predicted_tree.lat, predicted_tree.lng, 3)
                if nt is None:
                    TN_p += 1
                    break
                TP_p += 1
                self.tree_vis[nt.id] = True
                accuracy_p += predicted_tree.get_distance(latlng.LatLng(nt.lat, nt.lng))
        if TP_a > 0:
            precision_a = TP_a/(TP_a+TN_a)
            recall_a = TP_a/self.count
            accuracy_a /= TP_a
        if TP_p > 0:
            precision_p = TP_p/(TP_p+TN_p)
            recall_p = TP_p/self.count
            accuracy_p /= TP_p

        if filename != "":
            f = open(filename,"w")
            f.write("tree_cover_recall_of_labelled_trees = " + str(recall_a) + "\n")
            f.write("tree_cover_precision_of_labelled_trees = " + str(precision_a) + "\n")
            f.write("accuracy_of_geolocation_of_labelled_trees = " + str(accuracy_a) + "\n")
            f.write("tree_cover_recall_of_predicted_trees = " + str(recall_p) + "\n")
            f.write("tree_cover_precision_of_predicted_trees = " + str(precision_p) + "\n")
            f.write("accuracy_of_geolocation_of_predicted_trees = " + str(accuracy_p) + "\n")
            f.close()

        return recall_a, precision_a, accuracy_a, recall_p, precision_p, accuracy_p
