import random, time, statistics
from copy import deepcopy

import utils, parsing_utils, ir_utils
from metric import Metric
from constant import *
from pinput import *

NRUN = pinput["nrun"]
rand = random.Random(32)

##################### prioritzation

class Prio:
    def __init__(self, tcp, imgname, tinfo, pdata):
        self.tcp = tcp # tcp technique
        self.img = imgname # docker image config file name
        self.tinfo = tinfo # test data: Test(testname, test_result, testtime)
        self.pdata = pdata # prio data: code coverage, etc
        self.m = Metric([], imgname, {})


    def log_run(self, project, seed, res_arr):
            logging.info("[CPRIO]{\"project\": \"%s\", \"conf_chg\":\"%s\", \"tcp\":\"%s\", \"run\":\"%s\", \"scores\":\"%s\"}"%(
                project, self.img, self.tcp, seed, ",".join(map(str, res_arr))))


    def img_dependent(self, pdata):
        return pdata[self.img] if self.tcp in IMG_DEPENDENT else pdata


    def build_tests(self, rankdata):
        # only valid tests
        ret = []
        for tname, t in self.tinfo.items():
            cp = deepcopy(t)
            cp.rd = rankdata[tname]
            ret.append(cp)
        return ret


    def randomized(self):
        """randomized TCP"""
        rankdata = {t: 1 for t in self.tinfo}
        tests = self.build_tests(rankdata)
        self.run_helper(tests, desc=True)


    def total(self):
        """total TCP"""
        pdata = self.img_dependent(self.pdata)
        rankdata = {t: len(v) for t, v in pdata.items()}
        tests = self.build_tests(rankdata)
        self.run_helper(tests, desc=True)


    def qtf(self):
        """quickest time first TCP"""
        rankdata = {t: v["average"] for t, v in self.pdata.items()}
        tests = self.build_tests(rankdata)
        self.run_helper(tests, desc=False)


    def run_helper(self, tests, desc):
        """helper for randomized(), total(), qtf()"""
        result = []
        data = [deepcopy(t) for t in tests]
        for i in range(NRUN):
            self.m.pt = sorted(data, key=lambda x:(x.rd, bt()), reverse=desc)
            result.append(self.m.compute_metrics())
            rand.shuffle(data)
            self.log_run(project, i, result[-1])


    def additional(self):
        """additional TCP"""
        pdata = self.img_dependent(self.pdata)
        tests = self.build_tests(pdata)
        result = []
        for i in range(NRUN):
            self.m.pt = self.additional_helper(tests)
            result.append(self.m.compute_metrics())
            self.log_run(project, i, result[-1])


    def additional_helper(self, tests):
        """helper for additional()"""
        ptests = []
        data = {t.name: deepcopy(t) for t in tests}
        while len(data):
            # find the test with max additional coverage
            addt = max_add_test(data=data)
            ptests.append(addt)
            # update coverage
            del data[addt.name]
            for tname in list(data.keys()):
                data[tname].rd = data[tname].rd - addt.rd
            # if no test has new coverage
            no_new_coverage = True
            for x in data.values():
                if len(x.rd) > 0:
                    no_new_coverage = False
            if no_new_coverage:
                remain = list(data.values())
                rand.shuffle(remain)
                ptests += remain
                break
        return ptests


    def ir(self):
        """information-retrieval TCP"""
        testcases = set(self.tinfo.keys())
        rankdata = ir_utils.get_sim_di_q(self.tcp, self.img, self.pdata, testcases)
        tests = self.build_tests(rankdata)
        self.run_helper(tests, desc=True)


    ###################### hybrid

    def qtf_hybrid(self):
        """qtf time-sensitive hybrid TCP"""
        runtime = {t: self.pdata["d2"][t]["average"] for t in self.pdata["d2"]}
        tests = self.build_tests(runtime)
        result = []
        for i in range(NRUN):
            if self.tcp.endswith("_div"):
                self.m.pt = sorted(tests, key=lambda x:(x.rd/runtime[x.name], bt()))
            elif self.tcp.endswith("_bt"):
                self.m.pt = sorted(tests, key=lambda x:(x.rd, runtime[x.name], bt()))
            result.append(self.m.compute_metrics())
            self.log_run(project, i, result[-1])


    def randomized_hybrid(self):
        """randomized time-sensitive hybrid TCP"""
        rankdata = {t: 1 for t in self.tinfo}
        tests = self.build_tests(rankdata)
        result = []
        runtime = {t: self.pdata["d2"][t]["average"] for t in self.pdata["d2"]}
        for i in range(NRUN):
            for x in tests:
                x.rd = bt()
            if self.tcp.endswith("_div"):
                self.m.pt = sorted(tests, key=lambda x:(-x.rd/runtime[x.name], bt()))
            elif self.tcp.endswith("_bt"):
                self.m.pt = sorted(tests, key=lambda x:(x.rd, runtime[x.name], bt()))
            result.append(self.m.compute_metrics())
            self.log_run(project, i, result[-1])


    def additional_hybrid(self):
        """additional time-sensitive hybrid TCP"""
        pdata = self.img_dependent(self.pdata["d1"])
        tests = self.build_tests(pdata)
        result = []
        for i in range(NRUN):
            self.m.pt = self.additional_hybrid_helper(tests)
            result.append(self.m.compute_metrics())
            self.log_run(project, i, result[-1])


    def additional_hybrid_helper(self, tests):
        """helper for additional time-sensitive hybrid TCP"""
        ptests = []
        data = {t.name: deepcopy(t) for t in tests}
        runtime = {t: self.pdata["d2"][t]["average"] for t in self.pdata["d2"]}
        if self.tcp.endswith("_div"):
            while len(data):
                # find the test with max additional coverage
                addt = max_add_test(data=data, mode="div", runtime=runtime)
                ptests.append(addt)
                # update coverage
                del data[addt.name]
                for tname in list(data.keys()):
                    data[tname].rd = data[tname].rd - addt.rd
                # if no test has new coverage
                no_new_coverage = True
                for x in data.values():
                    if len(x.rd) > 0:
                        no_new_coverage = False
                if no_new_coverage:
                    remain = list(data.values())
                    rand.shuffle(remain)
                    ptests += remain
                    break
        elif self.tcp.endswith("_bt"):
            while len(data):
                # find the test with max additional coverage
                addt = max_add_test(data=data, mode="bt", runtime=runtime)
                ptests.append(addt)
                # update coverage
                del data[addt.name]
                for tname in list(data.keys()):
                    data[tname].rd = data[tname].rd - addt.rd
        return ptests


    def total_hybrid(self):
        """total time-sensitive hybrid TCP"""
        pdata = self.img_dependent(self.pdata["d1"])
        rankdata = {t: len(v) for t, v in pdata.items()}
        tests = self.build_tests(rankdata)
        self.hybrid_run_helper(tests)


    def ir_hybrid(self):
        """IR time-sensitive hybrid TCP"""
        irdata = self.pdata["d1"]
        testcases = set(self.tinfo.keys())
        sim_di_q = ir_utils.get_sim_di_q(self.tcp, self.img, irdata, testcases)
        rankdata = {}
        for test in testcases:
            rankdata[test] = sim_di_q[test]
        tests = self.build_tests(rankdata)
        self.hybrid_run_helper(tests)


    def hybrid_run_helper(self, tests):
        """helper for total_hybrid, ir_hybrid"""
        result = []
        data = [deepcopy(t) for t in tests]
        runtime = {t: self.pdata["d2"][t]["average"] for t in self.pdata["d2"]}
        for i in range(NRUN):
            if self.tcp.endswith("_div"):
                self.m.pt = sorted(data, key=lambda x:(-x.rd/runtime[x.name], bt()))
            elif self.tcp.endswith("_bt"):
                # descending score, ascending time
                self.m.pt = sorted(data, key=lambda x:(-x.rd, runtime[x.name], bt()))
            result.append(self.m.compute_metrics())
            rand.shuffle(data)
            self.log_run(project, i, result[-1])


################### utils

def max_add_test(data, mode=None, runtime=None):
    # find test in additional tcps
    # mode: div or bt
    new_test = rand.sample(list(data.values()), 1)[0]
    # basic additional
    if runtime == None:
        for x in data.values():
            temp = len(x.rd)
            curr_best = len(new_test.rd)
            if temp > curr_best or (temp==curr_best and bt()>bt()):
                new_test = x
    # div time or bt time
    else:
        if mode == "div":
            for x in data.values():
                temp = len(x.rd)/runtime[x.name]
                curr_best = len(new_test.rd)/runtime[new_test.name]
                if temp > curr_best or (temp==curr_best and bt()>bt()):
                    new_test = x
        elif mode == "bt":
            for x in data.values():
                temp = len(x.rd)
                curr_best = len(new_test.rd)
                temp_t = runtime[x.name]
                new_test_t = runtime[new_test.name]
                if temp > curr_best or (temp==curr_best and temp_t < new_test_t) \
                    or (temp==curr_best and temp_t < new_test_t and bt()>bt()):
                    new_test = x
    return new_test


def bt():
    # break tie
    return rand.uniform(0, 1)
