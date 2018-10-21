
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
import os
import datetime
import shutil
import heapq
import settingparser

class Simulator:

    def __init__(self, filename = "simulation.setting"):
        self.agents = []
        self.simulation_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.setting = settingparser.SettingParser(filename)
        self.time = 0
        self.event_heap = EventHeap(key=lambda x:x.time)

        if not os.path.exists("output"):
            os.makedirs("output")
        if not os.path.exists("output/"+self.simulation_id):
            os.makedirs("output/"+self.simulation_id)
        shutil.copyfile(filename,"output/"+self.simulation_id+"/"+filename)

    def run(self, end_time = 3600):
        # add event create_agent
        self.event_heap.push(Event("create_agent",np.random.poisson(self.setting.worker_arrival_interval,1)[0]))
        # add events output
        k = 1
        while True:
            t = k * self.setting.time_stamp
            if t >= end_time: break
            self.event_heap.push(Event("output",t))
            k += 1
        # add event finish
        self.event_heap.push(Event("finish",end_time))

        while True:
            # get first event from heap
            event = self.event_heap.pop()
            self.time = event.time

            if event.type == "create_agent":
                agent = self.create_agent()
                if len(agent.worker.task.uoas) > 0: # task has uoa.. meaning still has task to do
                    self.agents.append(agent)
                    # TODO: calculate uoa_finish_time
                    uoa_finish_time = 300
                    self.event_heap.push(Event("agent_finish_uoa",self.time + uoa_finish_time, agent))
                    self.event_heap.push(Event("agent_dropout",self.time + self.setting.dropout_time, agent))
                    self.event_heap.push(Event("create_agent",self.time + np.random.poisson(self.setting.worker_arrival_interval,1)[0]))

            if event.type == "agent_finish_uoa":
                if event.agent.finish_uoa():
                    # TODO: calculate uoa_finish_time
                    uoa_finish_time = 300
                    self.event_heap.push(Event("agent_finish_uoa",self.time + uoa_finish_time, event.agent))
                else:
                    if event.agent in self.agents:
                        self.agents.remove(event.agent)

            if event.type == "agent_dropout":
                if event.agent in self.agents:
                    self.agents.remove(event.agent)

            if event.type == "output":
                self.output()

            if event.type == "finish":
                self.output()
                return

    def create_agent(self):
        p = random.random()
        probability = 0
        for i in range(len(self.setting.worker_level_distribution)):
            probability += self.setting.worker_level_distribution[i]
            if i == len(self.setting.worker_level_distribution) - 1:
                probability = 1
            if p <= probability:
                agent = Agent(\
                self.setting.wm.new_worker(i, self.time),\
                self.setting.tf,\
                self.setting.worker_labelling_probability[i],\
                self.setting.worker_labelling_error[i],\
                self.setting.worker_labelling_time[i],\
                self.setting.worker_moving_distance[i],\
                self.setting.worker_moving_time[i])
                break
        return agent

    def output(self):
        for property in self.setting.output_properties:
            foldername = "output/"+self.simulation_id+"/"+property
            if property == "tree_cover":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                self.setting.tf.calc_performance(self.setting.rn, foldername+"/"+str(self.time)+".txt")
            elif property == "cost":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                f = open(foldername+"/"+str(self.time)+".txt","w")
                s = sum([worker.workload for worker in self.setting.wm.workers])
                f.write("cost = " + str(s*self.setting.payment_per_workload) + "\n")
                f.close()
            elif property == "worker_statistics":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                self.setting.wm.output_stat(foldername+"/"+str(self.time)+".txt")
            elif property == "task_statistics":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                self.setting.ta.output_stat(foldername+"/"+str(self.time)+".txt")
            #elif property == "UOA_statistic":
            #    if not os.path.exists(foldername):
            #        os.makedirs(foldername)
            elif property == "image":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                self.plot(foldername+"/"+str(self.time)+".png")

    def plot(self, filename = ''):
        self.setting.rn.plot_map(True)
        self.setting.rn.aggregator.plot_aggregated(True)
        for road in self.setting.rn.roads:
            road.predictor.plot(True)
        if len(filename) > 0:
            plt.savefig(filename)
        else:
            plt.show()


class Event:

    def __init__(self, type, time, agent = None):
        self.type = type
        self.time = time
        self.agent = agent

class EventHeap:

    def __init__(self, key=lambda x:x):
        self.key = key
        self._data = []
        self.count = 0

    def push(self, item):
        self.count += 1
        heapq.heappush(self._data, [self.key(item), self.count, item])

    def pop(self):
        return heapq.heappop(self._data)[2]

    def heapify(self):
        heapq.heapify(self._data)


class Agent:

    def __init__(self, worker, tf, lp, le, lt, md, mt):
    #treefinder, probability of label or not, standard deviation of labeling error, labeling time,
    #moving distance, moving time
        self.worker                 = worker
        self.tree_finder            = tf
        self.labeling_probability   = lp
        self.labeling_error         = le
        self.labeling_time          = lt
        self.moving_distance        = md
        self.moving_time            = mt
        self.status                 = 1 # 0:finished, 1:moving, 2:looking&labeling
        self.lasting_time           = 0 # lasting time of current status

    def finish_uoa(self):
        trees = []
        while True:
            uoa = self.worker.task.uoas[self.worker.uoa_id]
            ll = uoa.road.get_latlng(self.worker.cur_pos)
            nearby_trees = self.tree_finder.find_trees(ll.lat, ll.lng, 30)
            for tree in nearby_trees:
                if tree not in trees:
                    trees.append(tree)
            if self.worker.move(10) == False:
                break
        for tree in trees:
            if random.random() < self.labeling_probability:
                r = random.normalvariate(0,self.labeling_error)
                theta = random.random() * math.pi
                ll_tree = latlng.LatLng(tree.lat, tree.lng).get_latlng(r*math.cos(theta),r*math.sin(theta))
                self.worker.label(ll_tree.lat, ll_tree.lng)
        if self.worker.task_validation() > 0.9:
            self.worker.submit()
            return False
            # don't set next agent_finish_uoa
        self.worker.shift_uoa()
        self.worker.submit()
        return True
        # set next agent_finish_uoa

# main
#s = Simulator()
#s.run(18000)
#s.plot()
#
# sm = satellitemap.SatelliteMap(40.875, 40.700, -74.02, -73.91, 17)
# sm.download_all()
# sm.tree_map().show()

rn = roadnetwork.RoadNetwork("input/road_network_man.xml")
tf = treefinder.TreeFinder("input/trees_man.csv")
rn.plot_map(True)
tf.plot()
