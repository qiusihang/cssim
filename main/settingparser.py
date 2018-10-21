import roadnetwork
import treefinder
import worker
import taskassignment
import satellitemap

class SettingParser:

    def __init__(self, filename):
        self.rn = None
        self.tf = None
        self.sm = None
        self.ta = None

        self.expected_workload = 500
        self.payment_per_workload = 0.01
        self.dropout_time = 1000

        self.worker_arrival_interval = 30
        self.worker_level_distribution = [0.333, 0.333, 0.333]
        self.worker_labelling_time = [4, 3, 2]
        self.worker_moving_distance = [4, 3, 2]
        self.worker_moving_time = [1, 1, 1]
        self.worker_labelling_probability = [0.5, 0.7, 0.9]
        self.worker_labelling_error = [3, 2, 1]

        self.strategy = 0
        self.feedback_with_prediction = False
        self.prediction_with_satellite_map = False

        self.time_stamp = 100
        self.output_properties = []

        for line in open(filename):
            line = line.replace(' ','')
            line = line.replace('\n','')
            line = line.replace('\r','')
            if len(line) < 1:
                continue
            if line[0] != '#':
                args = line.split('=')
                if args[0] == "road_network":
                    self.rn = roadnetwork.RoadNetwork(args[1])
                elif args[0] == "ground_truth":
                    self.tf = treefinder.TreeFinder(args[1])
                elif args[0] == "satellite_map":
                    params = args[1].split(',')
                    params = [float(x) for x in params]
                    if len(params) > 4:
                        self.sm = satellitemap.SatelliteMap(params[0], params[1], params[2], params[3], params[4])

                elif args[0] == "expected_workload":
                    self.expected_workload = int(args[1])
                elif args[0] == "payment_per_workload":
                    self.payment_per_workload = float(args[1])
                elif args[0] == "dropout_time":
                    self.dropout_time = int(args[1])

                elif args[0] == "worker_arrival_interval":
                    params = args[1].split(',')
                    self.worker_arrival_interval = int(params[0])
                elif args[0] == "worker_level_distribution":
                    params = args[1].split(',')
                    self.worker_level_distribution = [float(x) for x in params]
                elif args[0] == "worker_labelling_time":
                    params = args[1].split(',')
                    self.worker_labelling_time = [float(x) for x in params]
                elif args[0] == "worker_moving_distance":
                    params = args[1].split(',')
                    self.worker_moving_distance = [float(x) for x in params]
                elif args[0] == "worker_moving_time":
                    params = args[1].split(',')
                    self.worker_moving_time = [float(x) for x in params]
                elif args[0] == "worker_labelling_probability":
                    params = args[1].split(',')
                    self.worker_labelling_probability = [float(x) for x in params]
                elif args[0] == "worker_labelling_error":
                    params = args[1].split(',')
                    self.worker_labelling_error = [float(x) for x in params]

                elif args[0] == "task_assignment_strategy":
                    if args[1] == "single_queue":
                        self.strategy = 0
                    elif args[1] == "multi_queue":
                        self.strategy = 3
                elif args[0] == "feedback_with_prediction":
                    if args[1] == "true" or args[1] == "True" or args[1] == "TRUE":
                        self.feedback_with_prediction = True
                    else:
                        self.feedback_with_prediction = False
                elif args[0] == "prediction_with_satellite_map":
                    if args[1] == "true" or args[1] == "True" or args[1] == "TRUE":
                        self.prediction_with_satellite_map = True
                    else:
                        self.prediction_with_satellite_map = False

                elif args[0] == "time_stamp":
                    self.time_stamp = int(args[1])
                elif args[0] == "output_properties":
                    self.output_properties = args[1].split(',')

        if self.rn == None or self.tf == None:
            return

        self.ta = taskassignment.TaskAssignment(self.rn, self.strategy, individual_workload = self.expected_workload)
        self.wm = worker.WorkerManager(self.rn, self.ta, self.sm)
        self.wm.prediction_with_satellite_map = self.prediction_with_satellite_map
