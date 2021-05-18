from constant import *

class Test:
    def __init__(self, name, res, ttime, srd=False):
        self.name = name
        self.res = res
        self.ttime = ttime
        self.rd = None # rank data
        self.srd = srd # show rank data


    def __str__(self):
        data = [self.name, self.res, self.ttime]
        if self.srd:
            rd = self.rd
            if type(self.rd) == []:
                rd = ",".join([str(x) for x in self.rd])
            data.append(rd)
        return "\t".join([str(x) for x in data])


EXCLUDES = set([x.strip() for x in open("special.list")])
def special_exclude(test):
    #  tests that cannot be instrumented by openclover 4.4.1
    testcls, testname = test.split("#")
    if testcls in EXCLUDES or test in EXCLUDES:
        return True
    return False
