import numpy as np
import latlng
from matplotlib import pyplot as plt

class Aggregator:

    def __init__(self):
        self.objects = []
        self.aggregated_objects = []

    def add_object(self, lat, lng):
        self.objects.append(latlng.LatLng(lat, lng))

    def aggregate(self, threshold=5):
        num = len(self.objects)
        px = np.zeros(num)
        py = np.zeros(num)
        rho = np.zeros(num)
        if num < 1: return
        for i in range(1,num):
            xy = self.objects[0].get_xy(self.objects[i])
            px[i] = xy.x
            py[i] = xy.y
        for i in range(num):
            s = 0
            for j in range(num):
                if (px[i]-px[j])**2 + (py[i]-py[j])**2 < threshold**2:
                    s = s + 1
            rho[i] = s + np.random.rand()*0.01

        dis = np.zeros(num)

        for i in range(num):
            m = 2147483647
            for j in range(num):
                if (rho[j] > rho[i]) and ((px[i]-px[j])**2 + (py[i]-py[j])**2 < m):
                    m = (px[i]-px[j])**2 + (py[i]-py[j])**2
            dis[i] = m

        self.aggregated_objects = []
        for i in range(num):
            if dis[i] > threshold**2:
                self.aggregated_objects.append(self.objects[i])

    def plot_original(self, holdon = False):
        num = len(self.objects)
        px = np.zeros(num)
        py = np.zeros(num)
        for i in range(num):
            px[i] = self.objects[i].lng
            py[i] = self.objects[i].lat
        plt.scatter(px,py,c='black',marker='x')
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
