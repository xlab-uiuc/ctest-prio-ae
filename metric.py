from constant import *
from pinput import *
import parsing_utils

METRIC_OPTIONS = pinput["metrics"]

FAILURE_MAP, FAULT_MAP = parsing_utils.failure_map()


class Metric:
    def __init__(self, ptests, imgname, testinfo):
        self.pt = ptests # prioritize tests
        self.img = imgname
        self.tf = testinfo
        self.ftests = FAILURE_MAP[self.img][C_EFFECTIVE]
        self.misconfs = FAULT_MAP[self.img]


    def APMD(self):
        sumTF = 0.0
        detected = set()
        for index, test in enumerate(self.pt):
            if test.res == "f":
                misconfs = set(self.ftests[test.name])
                n_newmisconf = len(misconfs - detected)
                if n_newmisconf > 0:
                    sumTF += (index + 1) * n_newmisconf
                    detected = detected.union(misconfs)
            if detected == self.misconfs:
                break
        
        nt = len(self.pt)
        return 1 - (sumTF/(nt*len(self.misconfs))) + (1/(2*nt))


    def APMDc(self):
        nt = len(self.pt)
        tte = [0] * nt # time till end
        tte[-1] = self.pt[-1].ttime
        for i in range(nt - 2, -1, -1):
            tte[i] = self.pt[i].ttime + tte[i + 1]

        detected = set()
        sum_m = 0.0
        for tf, test in enumerate(self.pt):
            if test.res == "f":
                misconfs = set(self.ftests[test.name])
                n_newmisconf = len(misconfs - detected)
                if n_newmisconf > 0:
                    sum_m += (tte[tf] - 0.5*test.ttime) * n_newmisconf
                    detected = detected.union(misconfs)
            # early termination
            if detected == self.misconfs:
                break

        sum_n = sum([t.ttime for t in self.pt])
        return sum_m / (sum_n * len(self.misconfs))


    def compute_metrics(self):
        metric = []
        
        # the classic
        if M_APMDC in METRIC_OPTIONS:
            metric.append(self.APMDc())
        if M_APMD in METRIC_OPTIONS:
            metric.append(self.APMD())

        return metric

