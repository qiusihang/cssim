# Only for simulation

class Tree:
    def __init__(self, category, lat, lng):
        self.category = category
        self.lat = lat
        self.lng = lng

class TreeFinder:

    def __init__(self, filename):
        self.tree_finder = []
        self.trees = []
        self.max_lat = -1e99
        self.min_lat = 1e99
        self.max_lng = -1e99
        self.min_lng = 1e99
        for line in open(filename,'r'):
            temp = line.split(';')
            tree = Tree(temp[0],float(temp[1]),float(temp[2]))
            self.trees.append(tree)
            self.max_lat = max(self.max_lat, tree.lat)
            self.min_lat = min(self.min_lat, tree.lat)
            self.max_lng = max(self.max_lng, tree.lng)
            self.min_lng = min(self.min_lng, tree.lng)
        self.n_lat = 100
        self.n_lng = 100
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

    def find_trees(self, lat, lng):
        trees = []
        i = int((lat - self.min_lat) * self.k_lat)
        j = int((lng - self.min_lng) * self.k_lng)
        for p in range(i-1,i+2):
            for q in range(j-1,j+2):
                if 0 <= p and p < self.n_lat and 0<=q and q < self.n_lng:
                    for tree in self.tree_finder[p][q]:
                        trees.append(tree)
        return trees
