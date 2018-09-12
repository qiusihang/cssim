import numpy as np
import latlng
from matplotlib import pyplot as plt

class Aggregator:

    def __init__(self):
        self.objects = []
        self.weights = []
        self.aggregated_objects = []

    def add_object(self, lat, lng, weight = 1):
        self.objects.append(latlng.LatLng(lat, lng))
        self.weights.append(weight)

    def aggregate(self, threshold_1 = 2.5, threshold_2 = 5):
    # threshold_1: radius for calculating density, threshold_2: min dis between trees
        num = len(self.objects)
        px = np.zeros(num)
        py = np.zeros(num)
        rho = np.zeros(num)
        alat = np.zeros(num)
        alng = np.zeros(num)
        if num < 1: return
        for i in range(1,num):
            xy = self.objects[0].get_xy(self.objects[i])
            px[i] = xy.x
            py[i] = xy.y
        for i in range(num):
            s = self.weights[i]
            t = 1
            ave_x = px[i] * self.weights[i]
            ave_y = py[i] * self.weights[i]
            for j in range(num):
                if i!=j and (px[i]-px[j])**2 + (py[i]-py[j])**2 < threshold_1 **2:
                    t += 1
                    s += self.weights[j]
                    ave_x += px[j] * self.weights[j]
                    ave_y += py[j] * self.weights[j]
            rho[i] = t + np.random.rand()*0.01
            ll = self.objects[0].get_latlng(ave_x/s, ave_y/s)
            alat[i] = ll.lat
            alng[i] = ll.lng

        dis = np.zeros(num)

        for i in range(num):
            m = 2147483647
            for j in range(num):
                if (rho[j] > rho[i]) and ((px[i]-px[j])**2 + (py[i]-py[j])**2 < m):
                    m = (px[i]-px[j])**2 + (py[i]-py[j])**2
            dis[i] = m

        self.aggregated_objects = []
        for i in range(num):
            if dis[i] > threshold_2**2:
                self.aggregated_objects.append(latlng.LatLng(alat[i],alng[i]))

    def plot_original(self, holdon = False):
        num = len(self.objects)
        px = np.zeros(num)
        py = np.zeros(num)
        for i in range(num):
            px[i] = self.objects[i].lng
            py[i] = self.objects[i].lat
        plt.scatter(px,py,c='pink',marker='x')
        if holdon==False: plt.show()

    def plot_aggregated(self, holdon = False):
        num = len(self.aggregated_objects)
        px = np.zeros(num)
        py = np.zeros(num)
        for i in range(num):
            px[i] = self.aggregated_objects[i].lng
            py[i] = self.aggregated_objects[i].lat
        plt.scatter(px,py,c='red',marker='x')
        if holdon==False: plt.show()
