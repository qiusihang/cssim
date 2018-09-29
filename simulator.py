
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
import settingparser

class Simulator:

    def __init__(self, filename = "simulation.setting"):
        self.agents = []
        self.simulation_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.setting = settingparser.SettingParser(filename)
        self.time = 0

        if not os.path.exists("output"):
            os.makedirs("output")
        if not os.path.exists("output/"+self.simulation_id):
            os.makedirs("output/"+self.simulation_id)
        shutil.copyfile(filename,"output/"+self.simulation_id+"/"+filename)

    def run(self, end_time = 3600):
        while True:
            self.propulse(self.setting.time_stamp)
            self.output()
            if self.time > end_time:
                break

    def propulse(self, steps = 1):
        new_agent_waiting_time = 0
        for i in range(steps):
            self.time += 1
            if new_agent_waiting_time < 1: # create a new agent
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
                if len(agent.worker.task.uoas) > 0: # task has uoa.. meaning still has task to do
                    self.agents.append(agent)
                    new_agent_waiting_time = np.random.poisson(self.setting.worker_arrival_interval,1)[0]
                else: # finshed
                    new_agent_waiting_time = 100000000
            else:
                new_agent_waiting_time -= 1

            for agent in self.agents:
                if self.time - agent.worker.strat_time > self.setting.dropout_time or agent.status == 0:
                    agent.worker.status = 1 # exit
                    self.agents.remove(agent)
                agent.run()

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
        #for road in self.setting.rn.roads:
        #    road.predictor.plot(True)
        if len(filename) > 0:
            plt.savefig(filename)
        else:
            plt.show()


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

    def run(self, steps = 1):
        for i in range(steps):
            if self.lasting_time > 0:
                self.lasting_time -= 1
                continue
            # here, lasting_time = 0, start new motion
            if self.status == 1:
                n = self.label()
                self.lasting_time = self.labeling_time * n
                self.status = 2
            elif self.status == 2:
                if self.worker.move(self.moving_distance) == True:
                    self.lasting_time = self.moving_time
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
        trees = self.tree_finder.find_trees(ll.lat, ll.lng, 10)
        n = 0
        for tree in trees:
            if random.random() < self.labeling_probability:
                r = random.normalvariate(0,self.labeling_error)
                theta = random.random() * math.pi
                ll_tree = latlng.LatLng(tree.lat, tree.lng).get_latlng(r*math.cos(theta),r*math.sin(theta))
                self.worker.label(ll_tree.lat, ll_tree.lng)
                n += 1
        return n

# main
s = Simulator()
s.run(5*3600)
