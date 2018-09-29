
import random
from road import *

class TaskAssignment:

    def __init__(self, rn, strategy = 0, individual_workload = 500):
        # strategy 0, 1: single-queue strategy; >1: multi-queue strategy
        self.rn = rn
        self.strategy = strategy
        self.individual_workload = individual_workload
        self.task_queues = [[] for i in range(strategy)] # (multi-queue strategy)
        self.task_queue = [] # (single-queue strategy)
        self.tasks = []

    def output_stat(self, filename):
        f = open(filename,"w")
        f.write(str(len(self.tasks))+"\n")
        for i in range(len(self.tasks)):
            task = self.tasks[i]
            f.write("\nID = "+str(i) + "\n")
            f.write("workers ("+str(len(task.workers))+") = ")
            for worker in task.workers:
                f.write(str(worker.id)+" ")
        f.close()

    def generate_task(self):
        task = Task()
        s = 0
        while s < self.individual_workload:
            index = -1
            m = 1e9
            uoa = None
            for road in self.rn.roads:
                road.predictor.predict()
                [index, minp, maxp] = road.predictor.get_lowest_centainty_uoa()
                if minp < m:
                    m = minp
                    uoa = road.uoas[index]
            if uoa is None:
                break
            task.add_uoa(uoa)
            uoa.priority += 100
            s += uoa.get_workload()
        self.tasks.append(task)
        return task

    def assign_task(self, worker):
        if self.strategy == 0 or self.strategy == 1:
            if len(self.task_queue) == 0:
                self.task_queue.append(self.generate_task())
            task = self.task_queue[0]
            task.assign_worker(worker)
            if len(task.workers) >= 3:
                self.task_queue.pop(0)

        if self.strategy > 1:
            if len(self.task_queues[worker.level]) == 0:
                task = self.generate_task()
                task.assign_worker(worker)
                for i in range(self.strategy):
                    if i != worker.level:
                        self.task_queues[i].append(task)
            else:
                task = self.task_queues[worker.level][0]
                task.assign_worker(worker)
                self.task_queues[worker.level].pop(0)

class Task:

    def __init__(self):
        self.uoas = []
        self.workers = []
        self.submision_times = []

    def assign_worker(self, worker):
        worker.task = self
        self.workers.append(worker)

    def add_uoa(self, uoa):
        self.uoas.append(uoa)
        self.submision_times.append(0)

    def print_task(self):
        for uoa in self.uoas:
            nodes = uoa.road.nodes
            s = 0
            print('ROAD (id='+str(uoa.road.ref)+', work amount='+str(uoa.get_work_amount())+'): ', end='')
            for i in range(uoa.pos_begin.index,uoa.pos_end.index+1):
                print('('+str(nodes[i].lat)+','+str(nodes[i].lng)+') ', end='')
            print('')
