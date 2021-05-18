import os, json, string, re
from gensim.summarization.bm25 import BM25
import parsing_utils
from constant import *
from pinput import *

#################### Building IR models

def build_query(params):
    result = ""
    for param in params:
        param_tokens = tokenize(param)
        result += (" " + " ".join(param_tokens))
    return result.strip()


def build_bm25(docsdata, level, ret_traindocs=False):
    """
    build array of traindocs for modeling [td1, td2, td3],
    and a map from tescase name to its testcls level doc pos in traindocs
    """
    if level == "cls":
        traindocs, indices = testcls_traindocs(docsdata)
    else:
        traindocs, indices = testcase_traindocs(docsdata)
    model = BM25(traindocs)
    ret = {"indices": indices, "model": model}
    if ret_traindocs:
        ret["traindocs"] = traindocs
    return ret



def get_sim_di_q(tcp, img, irdata, testcases):
    # get testcase score
    params = list(parsing_utils.get_file_params(img).keys())
    query = build_query(params).split()
    model = irdata["model"]# model: [d1, d2, d3...]
    indices = irdata["indices"] # indice: cls1: idx to d1, ...
    scores = model.get_scores(query)
    sim_di_q = {}
    for test in list(testcases):
        testkey = test.split("#")[0] if "cls" in tcp else test
        sim_di_q[test] = scores[indices[testkey]]
    return sim_di_q


######################## build document, traversing extended classes

def testcase_traindocs(docsdata):
    aggr_extclass(docsdata)
    tests = sorted(list(get_tests(docsdata)))
    indices = {}
    traindocs = []
    for idx, test in enumerate(tests):
        indices[test] = idx
        testcls, testcase = test.split("#")
        # each test's doc is its test body plus test file body shared by all tests
        doc = docsdata[testcls][testcase] + docsdata[testcls]["global"]
        traindocs.append(doc)
    return traindocs, indices


def testcls_traindocs(docsdata):
    traindocs = []
    indices = {}
    for idx, (testcls, clsdata) in enumerate(sorted(docsdata.items())):
        indices[testcls] = idx
        # each test's doc is the entire test file
        doc = []
        for key in clsdata:
            if key != "extendedClasses":
                doc += clsdata[key]
        traindocs.append(doc)
    return traindocs, indices


def aggr_extclass(docsdata):
    for testcls, clsdata in docsdata.items():
        if len(clsdata["extendedClasses"]) == 1:
            # collect chain of extended classes
            currcls = testcls
            chain = []
            while currcls:
                chain.append(currcls)
                currcls = find_extcls(docsdata.keys(), docsdata[currcls]["extendedClasses"])
            # traverse reversed chain, aggregate test infos
            for i in range(len(chain)-1, 0, -1):
                for key in docsdata[chain[i]]:
                    if key == "extendedClasses":
                        continue
                    elif key == "global":
                        docsdata[chain[i-1]][key] += docsdata[chain[i]][key]
                    else:
                        if key not in docsdata[chain[i-1]]:
                            docsdata[chain[i-1]][key] = []
                        docsdata[chain[i-1]][key] += docsdata[chain[i]][key]
        elif len(clsdata["extendedClasses"]) > 1:
            logging.info("[strange] more than one extended class", testcls)
        else:
            pass

def find_extcls(allcls, exts):
    # find the fully qualified name of the extend cls
    for extcls in exts:
        for c in allcls:
            if c.endswith("."+extcls):
                return c
    # possible to return the wrong cls with the same suffix but different qualname
    return None


def get_tests(docsdata):
    tests = set()
    for testcls in docsdata:
        for test in docsdata[testcls].keys():
            if test != "global" and test != "extendedClasses":
                tests.add(testcls + "#" + test)
    return tests


##################### string manipulation and serialization

def tokenize(s):
    result = ""
    buff = ""
    for word in s.split():
        for c in word:
            if c in string.ascii_lowercase:
                buff += c
            elif c in string.ascii_uppercase:
                # old buffer
                if buff != "":
                    # add to result only if len(buffer) > 1
                    if len(buff) > 1:
                        result += buff + " "
                    buff = ""
                # new buffer
                buff += c.lower()
            else:
                if buff != "":
                    if len(buff) > 1:
                        result += buff + " "
                    buff = ""
        if buff != "":
            if len(buff) > 1:
                result += buff + " "
            buff = ""
    return result.strip().split()
