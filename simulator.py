
import matplotlib.pyplot as plt
import numpy as np
import math
import latlng
import roadnetwork
import random
import treefinder
import worker
import taskassignment
import satellitemap

class Simulator:

    def __init__(self, wm, tf):
        # workermanager, treefinder
        self.wm = wm
        self.tf = tf
        self.agents = []

    def run(self, steps = 1):
        new_agent_waiting_time = 0
        for i in range(steps):
            if new_agent_waiting_time < 1:
                agent = Agent(wm.new_worker(), tf, 0.5, 1)
                self.agents.append(agent)
                new_agent_waiting_time = np.random.poisson(5,1)[0] # expected time interval is 5 seconds
            else:
                new_agent_waiting_time -= 1
            for agent in self.agents:
                agent.run()
                if agent.status == 0:
                    self.agents.remove(agent)

    def plot(self, filename = ''):
        self.wm.rn.plot_map(True)
        for road in self.wm.rn.roads:
            road.predictor.plot(True)
            road.aggregator.plot_aggregated(True)
        if len(filename) > 0:
            plt.savefig(filename)
        else:
            plt.show()


class Agent:

    def __init__(self, worker, tf, p, d):
    #treefinder, probability of label or not, standard deviation of labeling error
        self.worker = worker
        self.tf = tf
        self.p = p
        self.d = d
        self.status = 1 # 0:finished, 1:moving, 2:looking&labeling
        self.lasting_time = 0 # lasting time of current status

    def run(self, steps = 1):
        for i in range(steps):
            if self.lasting_time > 0:
                self.lasting_time -= 1
                continue
            # here, lasting_time = 0, start new motion
            if self.status == 1:
                n = self.label()
                self.lasting_time = 2 + 2 * n
                self.status = 2
            elif self.status == 2:
                if self.worker.move() == True:
                    self.lasting_time = 1
                    self.status = 1
                else:
                    if self.worker.task_validation() > 0.9:
                        self.worker.submit()
                        self.status = 0
                        return
                    self.worker.shift_uoa()
                    self.worker.submit()

    def label(self):
        # calculate current latlng
        uoa = self.worker.task.uoas[self.worker.uoa_id]
        ll = uoa.road.get_latlng(self.worker.cur_pos)
        plt.scatter(ll.lng, ll.lat, c='cyan', marker='o')
        # find three nearest trees
        trees = self.tf.find_trees(ll.lat, ll.lng)
        n = 0
        for tree in trees:
            if ll.get_distance(latlng.LatLng(tree.lat, tree.lng)) < 10:
                if random.random() < self.p:
                    ll_tree = latlng.LatLng(tree.lat, tree.lng).get_latlng(random.normalvariate(0,self.d),random.normalvariate(0,self.d))
                    self.worker.label(ll_tree.lat, ll_tree.lng)
                    n += 1
        return n

# main

rn = roadnetwork.RoadNetwork('road_network.xml')
ta = taskassignment.TaskAssignment(rn, strategy = 0)
sm = satellitemap.SatelliteMap(52.390, 52.365, 4.855, 4.890)
wm = worker.WorkerManager(rn, ta, sm)
tf = treefinder.TreeFinder('trees.csv')
s = Simulator(wm,tf)

#s.rn.plot_map(True)
#px = []
#py = []
#for tree in s.tf.trees:
#    px.append(tree.lng)
#    py.append(tree.lat)
#plt.scatter(px, py, marker='x', color='red')
#plt.show()

for i in range(10):
    s.run(100)
    #s.plot()
    s.plot("output/"+str(i)+".png")
