import matplotlib.pyplot as plt

# tree cover
recall_a = []
recall_p = []
precision_a = []
precision_p = []
acc_a = []
acc_p = []
cost = []
time_range = range(1,8)
for i in time_range:
    filename = str(i*1800)+".txt"
    for line in open("output/20180911153352/tree_cover/"+filename):
        line = line.replace(' ','')
        line = line.replace('\n','')
        line = line.replace('\r','')
        args = line.split('=')
        if args[0] == "tree_cover_recall_of_labelled_trees":
            recall_a.append(float(args[1])/0.8)
        if args[0] == "tree_cover_precision_of_labelled_trees":
            precision_a.append(float(args[1]))
        if args[0] == "tree_cover_recall_of_predicted_trees":
            recall_p.append(float(args[1])/0.8)
        if args[0] == "tree_cover_precision_of_predicted_trees":
            precision_p.append(float(args[1]))
    for line in open("output/20180911153352/accuracy_of_geolocation/"+filename):
        line = line.replace(' ','')
        line = line.replace('\n','')
        line = line.replace('\r','')
        args = line.split('=')
        if args[0] == "accuracy_of_geolocation_of_labelled_trees":
            acc_a.append(float(args[1]))
        if args[0] == "accuracy_of_geolocation_of_predicted_trees":
            acc_p.append(float(args[1]))
    for line in open("output/20180911153352/cost/"+filename):
        line = line.replace(' ','')
        line = line.replace('\n','')
        line = line.replace('\r','')
        args = line.split('=')
        cost.append(float(args[1]))

recall_a2 = []
recall_p2 = []
precision_a2 = []
precision_p2 = []
acc_a2 = []
acc_p2 = []
cost2 = []
for i in time_range:
    filename = str(i*1800)+".txt"
    for line in open("output/20180911162431/tree_cover/"+filename):
        line = line.replace(' ','')
        line = line.replace('\n','')
        line = line.replace('\r','')
        args = line.split('=')
        if args[0] == "tree_cover_recall_of_labelled_trees":
            recall_a2.append(float(args[1])/0.8)
        if args[0] == "tree_cover_precision_of_labelled_trees":
            precision_a2.append(float(args[1]))
        if args[0] == "tree_cover_recall_of_predicted_trees":
            recall_p2.append(float(args[1])/0.8)
        if args[0] == "tree_cover_precision_of_predicted_trees":
            precision_p2.append(float(args[1]))
    for line in open("output/20180911162431/accuracy_of_geolocation/"+filename):
        line = line.replace(' ','')
        line = line.replace('\n','')
        line = line.replace('\r','')
        args = line.split('=')
        if args[0] == "accuracy_of_geolocation_of_labelled_trees":
            acc_a2.append(float(args[1]))
        if args[0] == "accuracy_of_geolocation_of_predicted_trees":
            acc_p2.append(float(args[1]))
    for line in open("output/20180911162431/cost/"+filename):
        line = line.replace(' ','')
        line = line.replace('\n','')
        line = line.replace('\r','')
        args = line.split('=')
        cost2.append(float(args[1]))

plt.figure()
plt.subplot(221)
plt.plot(time_range, recall_a)
plt.plot(time_range, recall_a2)
plt.xlabel('time (*30min)')
plt.ylabel('tree cover recall')
plt.legend(['single-queue strategy','multi-queue strategy'])

plt.subplot(222)
plt.plot(time_range, precision_a)
plt.plot(time_range, precision_a2)
plt.xlabel('time (*30min)')
plt.ylabel('tree cover precision')
plt.legend(['single-queue strategy','multi-queue strategy'])

plt.subplot(223)
plt.plot(time_range, acc_a)
plt.plot(time_range, acc_a2)
plt.xlabel('time (*30min)')
plt.ylabel('labelling error deviation (m)')
plt.legend(['single-queue strategy','multi-queue strategy'])

plt.subplot(224)
#plt.plot(time_range, acc_p)
#plt.plot(time_range, acc_p2)
#plt.xlabel('time (*30min)')
#plt.ylabel('prediction error deviation (m)')
#plt.legend(['single-queue strategy','multi-queue strategy'])

plt.plot(cost, recall_a)
plt.plot(cost2, recall_a2)
plt.xlabel('cost (euro)')
plt.ylabel('tree cover recall')
plt.legend(['single-queue strategy','multi-queue strategy'])

plt.show()
