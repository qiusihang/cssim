
import xml.dom.minidom
import latlng
from road import *
import matplotlib.pyplot as plt

class RoadNetwork:

    def __init__(self, xml_filename):
        self.roads = []

        DOMTree = xml.dom.minidom.parse(xml_filename)
        root = DOMTree.documentElement
        xml_roads = root.getElementsByTagName("road")
        i = 0
        for xml_road in xml_roads:
            coords = []
            nodes = xml_road.getElementsByTagName("node")
            for node in nodes:
                coords.append( latlng.LatLng(float(node.getAttribute('lat')),float(node.getAttribute('lng'))) )
            self.roads.append(Road(i,coords))
            i += 1

    def plot_map(self, holdon = False):
        for road in self.roads:
            ndx = []
            ndy = []
            for node in road.nodes:
                ndy.append(node.lat)
                ndx.append(node.lng)
            plt.plot(ndx, ndy, c = 'blue')
            #plt.plot(ndx, ndy)
        if holdon == False: plt.show()

    def total_workload(self):
        s = 0
        for road in self.roads:
            l = len(road.nodes)
            for i in range(1,l):
                s += road.nodes[i-1].get_distance(road.nodes[i])
        return s


#rn = RoadNetwork('road_network.xml')
#t = rn.get_individual_task()
#t.print_task()
