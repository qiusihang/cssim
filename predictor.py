import math
import numpy as np
import latlng
import roadnetwork
import satellitemap
from matplotlib import pyplot as plt

class Predictor:

    def __init__(self, road, state_set = range(100)):
        self.road = road
        self.state_set = state_set
        self.dp = None
        self.update()

    def update(self):
        self.mc = [-1 for uoa in self.road.uoas]
        self.predicted_mc = [-1 for uoa in self.road.uoas]
        for i in range(len(self.road.uoas)):
            if self.road.uoas[i].worked_max_dis > self.road.uoas[i].worked_min_dis:
                self.mc[i] = 0
        object_pos = []
        for object in self.road.aggregator.aggregated_objects:
            object_pos.append(self.road.get_distance(object.lat, object.lng)[1])
        i = 0
        for dis in object_pos:
            while i < len(self.mc):
                uoa = self.road.uoas[i]
                if uoa.pos_begin.tdis <= dis and dis <= uoa.pos_end.tdis:
                    self.mc[i] += 1
                    break
                elif dis < uoa.pos_end.tdis:
                    i += 1
                else:
                    break

    def get_probability(self,x,y): #p(x|y)
        #x = x + 1
        #mean = mean + 1
        #mu = math.log(mean/math.sqrt(1+variance/mean/mean))
        #sigma = math.sqrt(math.log(1+variance/mean/mean))
        #return 1/(x * sigma * math.sqrt(2*math.pi)) * math.exp( - (math.log(x) - mu)**2/(2*sigma*sigma) )
        mu = y
        sigma = 1
        return 1/(math.sqrt(2*math.pi*sigma*sigma)) * math.exp( - (x-mu)**2/(2*sigma*sigma))

    def predict(self):
        self.update()
        if self.mc[0] == -1 or self.mc[-1] == -1:
            return
        self.dp = [{} for i in self.mc]
        self.pre = [{} for i in self.mc]
        for i in range(len(self.mc)):
            self.dp[i][self.mc[i]] = 0
            if i > 0:
                for s2 in self.state_set:
                    self.dp[i][s2] = 0
                    for s in self.dp[i-1]:
                        p = self.get_probability(s2,s) # p(s2|s)
                        if self.dp[i-1][s] * p > self.dp[i][s2]:
                            self.dp[i][s2] = self.dp[i-1][s] * p
                            self.pre[i][s2] = s
            if self.mc[i] >= 0:
                self.dp[i] = {self.mc[i]: 1}
        for i in range(len(self.mc)):
            j = len(self.mc) - i - 1
            self.predicted_mc[j] = self.mc[j]
            if self.dp[j][self.mc[j]] < 1:
                self.predicted_mc[j] = self.pre[j+1][self.predicted_mc[j+1]]
        self.update_priority()

    def update_priority(self):
        if len(self.mc) < 1:
            self.update()
        self.priority = [0 for i in self.mc]
        self.priority[0] = -1 + 1 / len(self.mc)
        self.priority[len(self.mc)-1] = -1 + 2 / len(self.mc)
        if len(self.mc) > 2:
            self.priority[int((len(self.mc)-1)/2)] = 1 + 1 / len(self.mc)
            o = 2
            for i in range(len(self.mc)):
                if self.priority[i] == 0:
                    self.priority[i] = 1 + o / len(self.mc)
                    o += 1
            for i in range(1, len(self.mc)):
                if self.mc[i] >= 0 and self.mc[i-1] < 0:
                    p = self.dp[i-1][self.predicted_mc[i-1]] * self.get_probability(self.predicted_mc[i-1], self.mc[i])
                    k = i-1
                    while k >= 0:
                        self.priority[k] = 1 - min(self.dp[k][self.predicted_mc[k]], p/self.dp[k][self.predicted_mc[k]])
                        k -= 1
                        if self.mc[k] >= 0:
                            break
        for i in range(len(self.mc)):
            k = int(self.road.uoas[i].priority/100)
            self.road.uoas[i].priority = self.priority[i] + k * 100

    def plot(self, holdon = False):
        px = []
        py = []
        for i in range(len(self.mc)):
            if self.mc[i] < 0 and self.predicted_mc[i] > 0:
                uoa = self.road.uoas[i]
                pos = uoa.pos_begin
                dis = uoa.get_distance() / self.predicted_mc[i]
                for j in range(self.predicted_mc[i]):
                    ll = uoa.road.get_latlng(pos)
                    px.append(ll.lng)
                    py.append(ll.lat)
                    pos = uoa.road.get_pos_from_to(pos, dis)
                    if pos.tdis < 0: break
        plt.scatter(px,py,c='green',marker='x')
        if holdon==False: plt.show()

#rn = roadnetwork.RoadNetwork("input/road_network.xml")
#import taskassignment
#ta = taskassignment.TaskAssignment(rn)
#p = Predictor(rn.roads[2], range(0,20))
#print(p.mc)
#p.mc[0] = 11
#p.mc[9] = 11
#p.predict()
#print(p.predicted_mc)
#p.update_priority()
#print(p.priority)
