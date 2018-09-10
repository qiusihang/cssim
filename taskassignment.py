
import heapq
import random
from road import *

class UoAHeap:

    def __init__(self, key=lambda x:x):
        self.key = key
        self._data = []
        self.count = 0

    def push(self, item):
        self.count += 1
        heapq.heappush(self._data, [self.key(item), self.count, item])

    def pop(self):
        return heapq.heappop(self._data)[2]


class TaskAssignment:

    def __init__(self, rn, strategy = 0, individual_workload = 500):
        # strategy 0, 1: single-queue strategy; >1: multi-queue strategy
        self.uoa_heap = UoAHeap(key=lambda x:x.priority+random.random())
        self.strategy = strategy
        self.individual_workload = individual_workload
        self.task_queues = [[] for i in range(strategy)] # (multi-queue strategy)
        self.task_queue = [] # (single-queue strategy)

        for road in rn.roads:
            cur_pos = LocInRoad(road,0,0)
            while True:
                next_pos = road.get_pos_from_to(cur_pos, 100)
                if next_pos.tdis < 0:
                    uoa = UoA(road,cur_pos,LocInRoad(road,len(road.nodes)-1,0))
                    self.uoa_heap.push(uoa)
                    break
                else:
                    uoa = UoA(road,cur_pos,next_pos)
                    self.uoa_heap.push(uoa)
                    cur_pos = next_pos

    def generate_task(self):
        task = Task()
        s = 0
        while s < self.individual_workload:
            uoa = self.uoa_heap.pop()
            if uoa.priority > 100:
                break
            task.add_uoa(uoa)
            uoa.priority += 100
            s += uoa.get_workload()
            self.uoa_heap.push(uoa)
        return task

    def assign_task(self, worker):
        if self.strategy == 0 or self.strategy == 1:
            if len(self.task_queue) == 0:
                self.task_queue.append(self.generate_task())
            task = self.task_queue[0]
            task.assign_worker(worker)
            worker.task = task
            if len(task.workers) >= 3:
                self.task_queue.pop(0)

        if self.strategy > 1:
            if len(self.task_queues[worker.level]) == 0:
                task = self.generate_task()
                worker.task = task
                task.assign_worker(worker)
                for i in range(self.strategy):
                    if i != worker.level:
                        self.task_queues[i].append(task)
            else:
                task = self.task_queues[worker.level][0]
                task.assign_worker(worker)
                worker.task = task
                self.task_queues[worker.level].pop(0)

class Task:

    def __init__(self):
        self.uoas = []
        self.workers = []

    def assign_worker(self, worker):
        self.workers.append(worker)

    def add_uoa(self, uoa):
        self.uoas.append(uoa)

    def print_task(self):
        for uoa in self.uoas:
            nodes = uoa.road.nodes
            s = 0
            print('ROAD (id='+str(uoa.road.ref)+', work amount='+str(uoa.get_work_amount())+'): ', end='')
            for i in range(uoa.pos_begin.index,uoa.pos_end.index+1):
                print('('+str(nodes[i].lat)+','+str(nodes[i].lng)+') ', end='')
            print('')
