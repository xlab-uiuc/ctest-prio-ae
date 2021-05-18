import re, json, glob, os, statistics, copy
import xml.etree.ElementTree as ET

from constant import *
from utils import *
from pinput import *
import ir_utils


PROJECT = pinput["project"]


################# parsing configuration file

def parse_conf_file(path):
    if PROJECT in [HCOMMON, HDFS, HBASE]:
        return parse_conf_file_xml(path)
    else:
        # parsing for alluxio and zookeeper conf file format
        if "no default configuration file" in path:
            return {}
        return parse_conf_file_properties(path)


def load_deprecate_config_map():
    deprecate_conf = {} # load deprecate map
    for line in open(DEPRECATE_CONF_MAP_FILE):
        deprecate_param, param = line.strip("\n").split("\t")
        deprecate_conf[deprecate_param] = param
    return deprecate_conf


def parse_conf_file_xml(path):
    deprecate_conf = load_deprecate_config_map()
    conf_map = {}
    fd = ET.parse(path)
    for kv in fd.getroot():
        # get key value pair
        cur_value = None
        cur_key = None
        for prop in kv:
            if prop.tag == "name":
                cur_key = re.sub('\n|\t', '', re.sub(' +', ' ', prop.text))
            elif prop.tag == "value" and cur_key:
                cur_value = prop.text
            else:
                pass
        if cur_key not in conf_map:
            if cur_key in deprecate_conf:
                cur_key = deprecate_conf[cur_key]
            conf_map[cur_key] = cur_value
    return conf_map


def parse_conf_file_properties(path):
    deprecate_conf = load_deprecate_config_map()
    conf_map = {}
    for line in open(path):
        if line.startswith("#"):
            continue
        seg = line.strip("\n").split("=")
        if len(seg) == 2:
            cur_key, cur_value = [x.strip() for x in seg]
            if cur_key not in conf_map:
                if cur_key in deprecate_conf:
                    cur_key = deprecate_conf[cur_key]
                conf_map[cur_key] = cur_value
    return conf_map


def find_matched_file(imgname, directory):
    for file in glob.glob(os.path.join(directory, "*")):
        if imgname in file:
            return file
    exit("no {} in {}".format(pattern, directory))


def get_file_params(imgname):
    # get the parameters in docker image imgname
    conf_path = find_matched_file(imgname, DOCKER_FILE_DIR.format(PROJECT))
    conf_map = parse_conf_file(conf_path)
    return conf_map


########################## ctest -> params

def reverse_ctest_map():
    mapping = json.load(open(CTEST_MAPPING.format(PROJECT)))
    data = {}
    for param in mapping:
        for test in mapping[param]:
            if test not in data:
                data[test] = set()
            data[test].add(param)
    return data


########################### parameter coverage


def param_id():
    mp = json.load(open(CTEST_MAPPING.format(PROJECT)))
    return {p: idx for idx, p in enumerate(list(mp.keys()))}


def param_coverage(change_aware, use_pid=True):
    pid = param_id()
    data = {}
    if change_aware:
        mapping = reverse_ctest_map()
        for file in glob.glob(os.path.join(TESTRESULT_DIR.format(PROJECT), TR_PATTERN)):
            imgname = re.findall(TR_REGEX, file)[0]
            file_params = set(get_file_params(imgname).keys())
            data[imgname] = {}
            tests = [x.strip("\n").split("\t")[0] for x in open(file)]
            for t in tests:
                ctestparam_of_t = mapping[t] if t in mapping else set()
                params = file_params.intersection(ctestparam_of_t)
                if len(params) > 0:
                    data[imgname][t] = params
    else:
        # sys-wide parameter coverage
        mapping = json.load(open(CTEST_MAPPING.format(PROJECT)))
        for param, tests in mapping.items():
            for test in tests:
                if test not in data:
                    data[test] = set()
                key = pid[param] if use_pid else param
                data[test].add(key)
    return data


#################### parsing test -> code coverage mapping
def code_coverage(level):
    path = ""
    if level == "method":
        path = METHOD_COVERAGE_FILE.format(PROJECT, PROJECT)
    elif level == "stmt":
        path = STMT_COVERAGE_FILE.format(PROJECT, PROJECT)
    mapping = json.load(open(path))
    mapping = {k: set(v) for k, v in mapping.items()}
    return mapping


####################### parsing config trace coverage

def config_trace_coverage(change_aware):
    cov = json.load(open(TRACE_FILE.format(PROJECT, PROJECT)))
    data = {}
    if change_aware:
        for file in glob.glob(os.path.join(TESTRESULT_DIR.format(PROJECT), TR_PATTERN)):
            img = re.findall(TR_REGEX, file)[0]
            chg_params = set(get_file_params(img).keys())
            tests = [x.strip("\n").split("\t")[0] for x in open(file)]
            data[img] = {}
            for test in tests:
                cov_params = cov[test].keys() if test in cov else set()
                params = chg_params.intersection(cov_params)
                data[img][test] = set()
                for param in params:
                    data[img][test] = data[img][test].union(cov[test][param])
    else:
        alltests = set(reverse_ctest_map().keys())
        for test in alltests:
            data[test] = set()
            if test in cov:
                for param in cov[test]:
                    data[test] = data[test].union(cov[test][param])
    return data


############################ parsing failure-to-fault mapping


def failure_map():
    all_failures = {}
    all_misconfs = {}
    for file in glob.glob(os.path.join(FAILURE_MAP_DIR.format(PROJECT), "*")):
        imgname = re.findall(FM_REGEX, file)[0]
        data = [x.strip("\n").split("\t") for x in open(file)]
        
        all_failures[imgname] = {C_FLAKY: {}, C_EFFECTIVE: {}, C_HARDCODED: {}}
        all_misconfs[imgname] = set()
        for row in data:
            test, ttype, misconfs = row
            misconfs = set([x for x in misconfs.split(",") if x != ""])
            all_failures[imgname][ttype][test] = misconfs
            if ttype == C_EFFECTIVE:
                all_misconfs[imgname] = all_misconfs[imgname].union(misconfs)

    assert all_failures != {}, "no failure-fault data for {}".format(PROJECT)
    return all_failures, all_misconfs



############################ parsing test running time under default configuation

def default_runtime():
    mapping = {}

    # if default runtime data not provided
    if not os.path.exists(EXECTIME_FILE.format(PROJECT, PROJECT)):
        return mapping

    data = [x.strip("\n").split("\t") for x in open(EXECTIME_FILE.format(PROJECT, PROJECT))]
    for row in data:
        testname = row[0]
        runtimes = [float(x) for x in row[1:6]]
        runtimes = [t if t != 0.0 else 0.001 for t in runtimes]
        mapping[testname] = {"all": runtimes, "average": statistics.mean(runtimes)}
    return mapping


####################### parse test file token and build bm25 model

def ir_model(level, gran):
    # gran: high or low
    # level: test case level, or test cls level
    docsdata = json.load(open(os.path.join(IRDOC_DIR, gran, PROJECT+".json")))
    return ir_utils.build_bm25(docsdata, level)


####################### parsing test result dataset

def parse_docker_dataset():
    testinfo = {}
    for file in glob.glob(os.path.join(TESTRESULT_DIR.format(PROJECT), TR_PATTERN)):
        imgname = re.findall(TR_REGEX, file)[0]
        data = [x.strip("\n").split("\t") for x in open(file)]
        testinfo[imgname] = {}
        for row in data:
            test, result, runtime = row[:3]
            testinfo[imgname][test] = [result, runtime]
    
    testinfo = rm_invalid_test(testinfo)

    dataset = {}
    failures, misconfs = failure_map()
    for imgname, testinfodata in sorted(testinfo.items()):
        perfile_tf = {}
        for testkey, testdata in testinfodata.items():
            result, runtime = testdata
            runtime = 0.001 if float(runtime) == 0 else float(runtime)
            perfile_tf[testkey] = Test(testkey, result, runtime)
        ntest = len(perfile_tf)
        nfailtest = len([1 for t in perfile_tf if perfile_tf[t].res == "f"])
        nparam = len(get_file_params(imgname))
        nmisconf = len(misconfs[imgname])
        if nfailtest > 0:
            dataset[imgname] = {
                "testinfo": copy.deepcopy(perfile_tf),
                "ntest": ntest,
                "nfailtest": nfailtest,
                "misconfs": misconfs[imgname],
                "nparam": nparam,
            }
        logging.info(">>>>conf_chg: {}, #params: {}, #misconfs: {}, #ctests: {}, #failed ctests: {}".format(
            imgname, nparam, nmisconf, ntest, nfailtest))
    return dataset

############################## filtering


def rm_invalid_test(testinfo):
    cc_stmt = set(code_coverage("stmt").keys())
    cc_method = set(code_coverage("method").keys())
    default_rt = set(default_runtime().keys())
    img_ctests = param_coverage(change_aware=True)
    failures, misconfs = failure_map() # per image

    testwithdata = cc_stmt.intersection(cc_method).intersection(default_rt)
    for imgname in testinfo:
        test_keys = set(testinfo[imgname].keys())
        ctests = set(img_ctests[imgname].keys())
        flaky = set(failures[imgname][C_FLAKY].keys())
        hardcoded = set(failures[imgname][C_HARDCODED].keys())
        # remove non ctest, test with no data
        test_keys = test_keys.intersection(ctests)
        test_keys = test_keys.intersection(testwithdata).intersection(default_rt)
        # remove hardcoded, flaky
        test_keys = (test_keys - flaky) - hardcoded
        # remove special exludes
        test_keys = set([t for t in test_keys if not special_exclude(t)])
        # remove tests with unfound runtime
        testinfo[imgname] = {t: testinfo[imgname][t] \
            for t in test_keys if testinfo[imgname][t][1] != "UNFOUND"}
    return testinfo
