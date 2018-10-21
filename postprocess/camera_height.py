import os
import math
import latlng
import raycast
import treefinder
import matplotlib.pyplot as plt

userid = "testjnbi2yw6nf280th6h";
tf = treefinder.TreeFinder("files/trees.csv")

filename = "files/users/"+ userid + "list.csv"
if not os.path.exists(filename):
    url = "https://urbanmapping.tk/urbanmapping/export_list.php?userid="+userid
    r = requests.get(url)
    with open(filename,'wb') as f:
        f.write(r.content)

labels = []
for line in open(filename):
    data = line.split(',')
    if len(data) < 8: continue
    labels.append({\
        "cam_pos":latlng.LatLng(float(data[0]),float(data[1])),\
        "heading":float(data[2]),\
        "pitch":float(data[3]),\
        "fovy":float(data[4]),
        "bbox":[float(data[5]),float(data[6]),float(data[7]),float(data[8])]\
    })

#labels = [labels[0], labels[2], labels[4], labels[5]]
#
# min = 999999
# for h in range(100,300):
#     eh = h/100
#     s = 0
#     for label in labels:
#         norm_screen_x = (label["bbox"][0] + label["bbox"][2]) - 1
#         norm_screen_y = 1 - label["bbox"][3] * 2
#         r = raycast.Raycast(label["heading"], label["pitch"], norm_screen_x, norm_screen_y, label["fovy"], 640/480)
#         pos = r.get_latlng(label["cam_pos"].lat,label["cam_pos"].lng, eh)
#         s += label["real_pos"].get_distance(latlng.LatLng(pos["lat"],pos["lng"]))**2
#     if s < min:
#         min = s
#         oh = eh
#
# print(oh)

numerator = 0
denominator = 0
for label in labels:
    norm_screen_x = (label["bbox"][0] + label["bbox"][2]) - 1
    norm_screen_y = 1 - label["bbox"][3] * 2
    r = raycast.Raycast(label["heading"], label["pitch"], norm_screen_x, norm_screen_y, label["fovy"], 640/480)

    # Find the nearest tree
    ll = r.get_latlng(label["cam_pos"].lat,label["cam_pos"].lng, 2)
    d = 10
    tree = None
    while True:
        tree = tf.find_the_nearest_tree(ll["lat"], ll["lng"], d)
        if tree == None:
            d += 10
        else:
            break
    label["real_pos"] = latlng.LatLng(tree.lat,tree.lng)

    pos = label["cam_pos"].get_xy(label["real_pos"])
    heading = ((360 - label['heading']) + 90)%360
    c1 = r.get_distance(1) * math.cos(heading/180.0*math.pi)
    c2 = r.get_distance(1) * math.sin(heading/180.0*math.pi)

    if c1 is not None and c2 is not None:
        numerator += pos.x * c1 + pos.y * c2
        denominator += c1 ** 2 + c2 ** 2
print(numerator/denominator)
print()
oh = numerator/denominator

x1 = []
y1 = []
x2 = []
y2 = []
for label in labels:
    norm_screen_x = (label["bbox"][0] + label["bbox"][2]) - 1
    norm_screen_y = 1 - label["bbox"][3] * 2
    r = raycast.Raycast(label["heading"], label["pitch"], norm_screen_x, norm_screen_y, label["fovy"], 640/480)
    pos = r.get_latlng(label["cam_pos"].lat,label["cam_pos"].lng, oh)
    #print(label["real_pos"].get_distance(latlng.LatLng(pos["lat"],pos["lng"])))
    x1.append(pos["lng"])
    y1.append(pos["lat"])
    x2.append(label["real_pos"].lng)
    y2.append(label["real_pos"].lat)
plt.scatter(x1,y1)
plt.scatter(x2,y2)
plt.show()
