import os, copy, glob, re

import parsing_utils
from constant import *
from pinput import *

PROJECT = pinput["project"]



def testresult_files():
    return glob.glob(os.path.join(TESTRESULT_DIR.format(PROJECT), TR_PATTERN))


def splited_tests(file):
    return [x.strip("\n").split("\t") for x in open(file)]


def pf_all():
    # pf(failed test t) is determined by #files t failed on
    freq = {}
    failures, misconfs = parsing_utils.failure_map()
    for img in failures:
        for t, misconfs in failures[img][C_EFFECTIVE].items():
            if t not in freq:
                freq[t] = set()
            freq[t].add(img)

    # remove each file from its failure frequency
    pf = {}
    for file in testresult_files():
        tests = [t[0] for t in splited_tests(file)]
        img = re.findall(TR_REGEX, file)[0]
        pf[img] = {}
        for t in tests:
            pf[img][t] = set()
            if t in freq:
                pf[img][t] = freq[t] - set([img])
    return pf


def pf_dp():
    # pf(failed test t) is determined by all params in the change where t failed on

    # load peer config failure frequency
    freq = {}
    failures, misconfs = parsing_utils.failure_map()
    for img in failures:
        for t, misconfs in failures[img][C_EFFECTIVE].items():
            params = set([k for k in parsing_utils.get_file_params(img).keys()])
            if t not in freq:
                freq[t] = {}
            # failed test -> param in change -> change that failed the test
            for p in params:
                if p not in freq[t]:
                    freq[t][p] = set()
                freq[t][p].add(img)
    return build_pf(freq)


def pf_pc():
    # pf(failed test t) is determined by all param get by t in the change where t failed on
    readparams = parsing_utils.param_coverage(change_aware=False, use_pid=False)
    # load peer config failure frequency
    freq = {}
    failures, misconfs = parsing_utils.failure_map()
    for img in failures:
        for t, misconfs in failures[img][C_EFFECTIVE].items():
            params = set([k for k in parsing_utils.get_file_params(img).keys()])
            if t not in freq:
                freq[t] = {}
            # failed test -> param get (in change) -> changes where t fails
            for p in params.intersection(readparams[t]):
                if p not in freq[t]:
                    freq[t][p] = set()
                freq[t][p].add(img)
    return build_pf(freq)


def pf_rc():
    """
    pf(failed test t) is determined by the root cause param in the change where t fails
    root cause is localized through manual inspection
    """

    freq = {}
    failures, misconfs = parsing_utils.failure_map()
    for img in failures:
        for t, rootcauses in failures[img][C_EFFECTIVE].items():
            if t not in freq:
                freq[t] = {}
            for p in rootcauses:
                if p not in freq[t]:
                    freq[t][p] = set()
                freq[t][p].add(img)
    return build_pf(freq)


def build_pf(freq):
    # remove each file from its failure frequency
    pf = {}
    for file in testresult_files():
        tests = [t[0] for t in splited_tests(file)]
        img = re.findall(TR_REGEX, file)[0]
        params = set([k for k in parsing_utils.get_file_params(img).keys()])
        pf[img] = {}
        for t in tests:
            pf[img][t] = {}
            if t in freq:
                # ignore params not in the current change
                for p in params.intersection(freq[t].keys()):
                    # exclude current change from its own peer failures
                    pf[img][t][p] = freq[t][p] - set([img])
    # convert to failed test -> #peer failures
    for img in pf:
        for t in pf[img]:
            failed_imgs = set()
            for p in pf[img][t]:
                failed_imgs = failed_imgs.union(pf[img][t][p])
            # pf[img][t] = len(failed_imgs)
            pf[img][t] = failed_imgs
    return pf


def pf_pcc():
    # pf(failed test t) is determined by all param get by t in the change where t failed on
    readparams = parsing_utils.param_coverage(change_aware=False, use_pid=False)
    # load peer config failure frequency
    freq = {}
    failures, misconfs = parsing_utils.failure_map()
    for img in failures:
        for t, misconfs in failures[img][C_EFFECTIVE].items():
            params = set([k for k in parsing_utils.get_file_params(img).keys()])
            if t not in freq:
                freq[t] = {}
            # failed test -> param get (in change) -> changes where t fails
            for p in params.intersection(readparams[t]):
                if p not in freq[t]:
                    freq[t][p] = set()
                freq[t][p].add(img)
    return build_pf_cov(freq)


def pf_rcc():
    """
    pf(failed test t) is determined by the root cause param in the change where t fails
    root cause is localized through manual inspection
    """

    freq = {}
    failures, misconfs = parsing_utils.failure_map()
    for img in failures:
        for t, rootcauses in failures[img][C_EFFECTIVE].items():
            if t not in freq:
                freq[t] = {}
            for p in rootcauses:
                if p not in freq[t]:
                    freq[t][p] = set()
                freq[t][p].add(img)
    return build_pf_cov(freq)


def build_pf_cov(freq):
    # remove each file from its failure frequency
    pf = {}
    for file in testresult_files():
        tests = [t[0] for t in splited_tests(file)]
        img = re.findall(TR_REGEX, file)[0]
        params = set([k for k in parsing_utils.get_file_params(img).keys()])
        pf[img] = {}
        for t in tests:
            pf[img][t] = {}
            if t in freq:
                # ignore params not in the current change
                for p in params.intersection(freq[t].keys()):
                    # exclude current change from its own peer failures
                    pf[img][t][p] = freq[t][p] - set([img])
    # convert to failed test -> #peer failures
    for img in pf:
        for t in pf[img]:
            pf[img][t] = set([x for x in pf[img][t].keys()])
    return pf