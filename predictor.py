
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
        self.update()

    def update(self):
        self.mc = [-1 for uoa in self.road.uoas]
        self.predicted_mc = [-1 for uoa in self.road.uoas]
        for i in range(len(self.road.uoas)):
            if self.road.uoas[i].worked_max_dis > self.road.uoas[i].worked_min_dis:
                self.mc[i] = 0
        for object in self.road.aggregator.aggregated_objects:
            object_pos = self.road.get_distance(object.lat, object.lng)[1]
            for i in range(len(self.road.uoas)):
                uoa = self.road.uoas[i]
                if uoa.pos_begin.tdis <= object_pos and object_pos <= uoa.pos_end.tdis:
                    self.mc[i] += 1
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

    def get_lowest_centainty_uoa(self):
        if self.mc[0] < 0:
            return [0,-len(self.mc),0] # longer the road is, lower uncertainly value will be given
        if self.mc[-1] < 0:
            return [len(self.mc)-1,-len(self.mc),0]
        minp = 1e99
        k = -1
        for i in range(1, len(self.mc)):
            if self.mc[i] >= 0 and self.mc[i-1] < 0:
                p = self.dp[i-1][self.predicted_mc[i-1]] * self.get_probability(self.predicted_mc[i-1], self.mc[i])
                if p < minp:
                    minp = p
                    k = i
        if k > 0:
            k = k-1
            index = k-1
            maxp = 0
            while k >= 0:
                ep = min(self.dp[k][self.predicted_mc[k]], minp/self.dp[k][self.predicted_mc[k]])
                if ep > maxp:
                    maxp = ep
                    index = k
                k -= 1
                if self.mc[k] >= 0:
                    break
            return [index, minp, maxp]
        return None

#rn = roadnetwork.RoadNetwork("input/road_network.xml")
#p = Predictor(rn.roads[2], range(0,20))
#print(p.mc)
#p.mc[0] = 11
#p.mc[9] = 11
#p.predict()
#print(p.predicted_mc)
#print(p.get_lowest_centainty_uoa())
