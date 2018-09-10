
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

class Simulator:

    def __init__(self, filename = "simulation.setting"):
        self.read_setting(filename)
        self.agents = []
        self.simulation_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        if not os.path.exists("output"):
            os.makedirs("output")
        if not os.path.exists("output/"+self.simulation_id):
            os.makedirs("output/"+self.simulation_id)

    def read_setting(self, filename = "simulation.setting"):
        self.rn = None
        self.tf = None
        self.sm = None
        self.ta = None

        self.expected_workload = 500
        self.payment_per_workload = 0.01
        self.dropout_time = 1000

        self.worker_arrival_interval = 30
        self.worker_level_distribution = [0.3, 0.4, 0.3]
        self.worker_labelling_time = [4, 3, 2]
        self.worker_moving_distance = [4, 3, 2]
        self.worker_moving_time = [1, 1, 1]
        self.worker_labelling_probability = [0.3, 0.5, 0.8]
        self.worker_labelling_error = [3, 2, 1]

        self.strategy = 0
        self.feedback_with_prediction = False
        self.prediction_with_satellite_map = False

        self.time_stamp = 100
        self.output_properties = []

        for line in open('simulation.setting'):
            line = line.replace(' ','')
            line = line.replace('\n','')
            line = line.replace('\r','')
            if len(line) < 1:
                continue
            if line[0] != '#':
                args = line.split('=')
                if args[0] == "road_network":
                    self.rn = roadnetwork.RoadNetwork(args[1])
                elif args[0] == "ground_truth":
                    self.tf = treefinder.TreeFinder(args[1])
                elif args[0] == "satellite_map":
                    params = args[1].split(',')
                    params = [float(x) for x in params]
                    if len(params) > 4:
                        self.sm = satellitemap.SatelliteMap(params[0], params[1], params[2], params[3], params[4])

                elif args[0] == "expected_workload":
                    self.expected_workload = int(args[1])
                elif args[0] == "payment_per_workload":
                    self.payment_per_workload = float(args[1])
                elif args[0] == "dropout_time":
                    self.dropout_time = int(args[1])

                elif args[0] == "worker_arrival_interval":
                    params = args[1].split(',')
                    self.worker_arrival_interval = int(params[0])
                elif args[0] == "worker_level_distribution":
                    params = args[1].split(',')
                    self.worker_level_distribution = [float(x) for x in params]
                elif args[0] == "worker_labelling_time":
                    params = args[1].split(',')
                    self.worker_labelling_time = [float(x) for x in params]
                elif args[0] == "worker_moving_distance":
                    params = args[1].split(',')
                    self.worker_moving_distance = [float(x) for x in params]
                elif args[0] == "worker_moving_time":
                    params = args[1].split(',')
                    self.worker_moving_time = [float(x) for x in params]
                elif args[0] == "worker_labelling_probability":
                    params = args[1].split(',')
                    self.worker_labelling_probability = [float(x) for x in params]
                elif args[0] == "worker_labelling_error":
                    params = args[1].split(',')
                    self.worker_labelling_error = [float(x) for x in params]

                elif args[0] == "task_assignment_strategy":
                    if args[1] == "single_queue":
                        self.strategy = 0
                    elif args[1] == "multi_queue":
                        self.strategy = 3
                elif args[0] == "feedback_with_prediction":
                    if args[1] == "true" or args[1] == "True" or args[1] == "TRUE":
                        self.feedback_with_prediction = True
                    else:
                        self.feedback_with_prediction = False
                elif args[0] == "prediction_with_satellite_map":
                    if args[1] == "true" or args[1] == "True" or args[1] == "TRUE":
                        self.prediction_with_satellite_map = True
                    else:
                        self.prediction_with_satellite_map = False

                elif args[0] == "time_stamp":
                    self.time_stamp = int(args[1])
                elif args[0] == "output_properties":
                    self.output_properties = args[1].split(',')

        if self.rn == None or self.tf == None:
            return

        self.ta = taskassignment.TaskAssignment(self.rn, self.strategy, individual_workload = self.expected_workload)
        self.wm = worker.WorkerManager(self.rn, self.ta, self.sm)
        self.wm.prediction_with_satellite_map = self.prediction_with_satellite_map

    def run(self, end_time = 3600):
        while True:
            self.propulse(self.time_stamp)
            self.output()
            if self.wm.time > end_time:
                break

    def propulse(self, steps = 1):
        new_agent_waiting_time = 0
        for i in range(steps):
            self.wm.time += 1
            if new_agent_waiting_time < 1:
                level = random.random()
                threshold = 0
                for i in range(len(self.worker_level_distribution)):
                    threshold += self.worker_level_distribution[i]
                    if i == len(self.worker_level_distribution) - 1 and threshold < 1:
                        threshold = 1
                    if level <= threshold:
                        agent = Agent(self.wm.new_worker(i), self.tf, \
                        self.worker_labelling_probability[i], self.worker_labelling_error[i],self.worker_labelling_time[i],\
                        self.worker_moving_distance[i], self.worker_moving_time[i])
                        break
                if len(agent.worker.task.uoas) > 0: # task has uoa.. meaning still has task to do
                    self.agents.append(agent)
                    new_agent_waiting_time = np.random.poisson(self.worker_arrival_interval,1)[0]
                else:
                    new_agent_waiting_time = 100000000
            else:
                new_agent_waiting_time -= 1
            for agent in self.agents:
                if agent.worker.wm.time - agent.worker.strat_time > self.dropout_time or agent.status == 0:
                    agent.worker.status = 1
                    self.agents.remove(agent)
                agent.run()

    def output(self):
        for property in self.output_properties:
            foldername = "output/"+self.simulation_id+"/"+property
            recall_a = None
            recall_p = None
            precision_a = None
            precision_p = None
            acc_a = None
            acc_p = None
            if property == "tree_cover":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                f = open(foldername+"/"+str(self.wm.time)+".txt","w")
                if recall_a is None:
                    recall_a, precision_a, acc_a, recall_p, precision_p, acc_p = self.tf.calc_performance(self.rn)
                f.write("tree_cover_recall_of_labelled_trees = " + str(recall_a) + "\n")
                f.write("tree_cover_precision_of_labelled_trees = " + str(precision_a) + "\n")
                f.write("tree_cover_recall_of_predicted_trees = " + str(recall_p) + "\n")
                f.write("tree_cover_precision_of_predicted_trees = " + str(precision_p) + "\n")
                f.close()
            elif property == "accuracy_of_geolocation":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                f = open(foldername+"/"+str(self.wm.time)+".txt","w")
                if acc_a is None:
                    recall_a, precision_a, acc_a, recall_p, precision_p, acc_p = self.tf.calc_performance(self.rn)
                f.write("accuracy_of_geolocation_of_labelled_trees = " + str(acc_a) + "\n")
                f.write("accuracy_of_geolocation_of_predicted_trees = " + str(acc_p) + "\n")
                f.close()
            elif property == "cost":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                f = open(foldername+"/"+str(self.wm.time)+".txt","w")
                s = 0
                for worker in self.wm.workers:
                    s += worker.workload
                f.write("cost = " + str(s*self.payment_per_workload) + "\n")
                f.close()
            elif property == "worker_statistics":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                f = open(foldername+"/"+str(self.wm.time)+".txt","w")
                f.write(str(len(self.wm.workers))+"\n")
                for i in range(len(self.wm.workers)):
                    worker = self.wm.workers[i]
                    f.write("\nID = "+str(worker.id) + "\n")
                    f.write("level = "+str(worker.level) + "\n")
                    f.write("workeload = "+str(worker.workload) + "\n")
                    f.write("complete = "+str(worker.task_validation()) + "\n")
                    f.write("labels = "+str(worker.labels) + "\n")
                    f.write("status = "+str(worker.status) + "\n")
                f.close()
            elif property == "task_statistics":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
            elif property == "UOA_statistic":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
            elif property == "image":
                if not os.path.exists(foldername):
                    os.makedirs(foldername)
                self.plot(foldername+"/"+str(self.wm.time)+".png")

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

    def __init__(self, worker, tf, lp, le, lt, md, mt):
    #treefinder, probability of label or not, standard deviation of labeling error, labeling time,
    #moving distance, moving time
        self.worker = worker
        self.tf = tf
        self.lp = lp
        self.le = le
        self.lt = lt
        self.md = md
        self.mt = mt
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
                self.lasting_time = self.lt * n
                self.status = 2
            elif self.status == 2:
                if self.worker.move(self.md) == True:
                    self.lasting_time = self.mt
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
        trees = self.tf.find_trees(ll.lat, ll.lng, 10)
        n = 0
        for tree in trees:
            if random.random() < self.lp:
                ll_tree = latlng.LatLng(tree.lat, tree.lng).get_latlng(random.normalvariate(0,self.le),random.normalvariate(0,self.le))
                self.worker.label(ll_tree.lat, ll_tree.lng)
                n += 1
        return n

# main
s = Simulator()
s.run(5*3600)
