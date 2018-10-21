import os
import latlng
import raycast
import datetime
import requests
import treefinder

log = {}
months = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
tf = tf.TreeFinder("../main/input/trees.csv")

tree_amount = 7
cam_height = 1.66

for userid in open("files/user_list.txt"):
    userid = userid.replace("\n","")

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
    e = 0
    count = {}
    for label in labels:
        norm_screen_x = (label["bbox"][0] + label["bbox"][2]) - 1
        norm_screen_y = 1 - label["bbox"][3] * 2
        r = raycast.Raycast(label["heading"], label["pitch"], norm_screen_x, norm_screen_y, label["fovy"], 640/480)
        ll = r.get_latlng(label["cam_pos"].lat,label["cam_pos"].lng, cam_height)
        d = 10
        while True:
            tree = tf.find_the_nearest_tree(ll["lat"], ll["lng"], d)
            if tree == None:
                d += 10
            else:
                e += latlng.LatLng(tree.lat, tree.lng).get_distance(latlng.LatLng(ll["lat"], ll["lng"]))
                if tree.id in count.keys():
                    count[tree.id] += 1
                else:
                    count[tree.id] = 1
                break
    if len(labels) > 0: e /= len(labels)

    m = 0
    for key in count.keys():
        m = max(m, count[key])
    hist = [0 for i in range(m+1)]
    hist[0] = max(0, tree_amount - len(count.keys()))
    for key in count.keys():
        hist[count[key]] += 1
    s = sum(hist)
    hist = [i/s for i in hist]

    filename = "files/users/"+ userid + "log.txt"
    if not os.path.exists(filename):
        url = "https://urbanmapping.tk/urbanmapping/export_log.php?userid="+userid
        r = requests.get(url)
        with open(filename,'wb') as f:
            f.write(r.content)

    log[userid] = []
    length = 0
    for line in open(filename, encoding = "utf-8"):
        if len(line) < 10: continue
        if line[0]=='P' and line[1]=='A':
            params = line.split('&')

            posstr = params[0]
            posstr = posstr.replace("PANO CHANGED:(","")
            posstr = posstr.replace(")","")
            ll = posstr.split(',')
            pos = latlng.LatLng(float(ll[0]),float(ll[1]))

            heading = float(params[1])

            pitch = float(params[2])

            if params[3].isdigit():
                zoom = float(params[3])

            timestr = params[4].split(' ')
            hms = timestr[4].split(':')
            time = datetime.datetime(int(timestr[3]), months[timestr[1]], int(timestr[2]), int(hms[0]), int(hms[1]), int(hms[2]))

            log[userid].append({"pos":pos, "heading":heading, "pitch":pitch, "zoom":zoom, "time":time})

            length = max(length, log[userid][0]["pos"].get_distance(pos))

    log[userid].sort(key=lambda x:x["time"])
    execution_time = (log[userid][-1]["time"] - log[userid][1]["time"]).total_seconds()
    #instruction_time = (log[userid][1]["time"] - log[userid][0]["time"]).total_seconds()

    print('userid:', end='')
    print(userid)
    print('err:', end='')
    print(e)
    print('hist:', end='')
    print(hist)
    print('execution_speed [s/100m]:',end='')
    print(execution_time/length*100)
    print()
