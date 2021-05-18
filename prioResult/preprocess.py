import sys, re, statistics, json, os, glob
import argparse


sys.path.insert(1, "..")
from constant import *
import tcp_groups

PRIODATA_DIR = "prioData"
HSDDATA_DIR = "hsdTable"
os.makedirs(PRIODATA_DIR, exist_ok=True)
os.makedirs(HSDDATA_DIR, exist_ok=True)


########################### utils

def dir_and_name(fpath):
    fdir = os.path.dirname(fpath)
    fname = os.path.basename(fpath)
    return fdir, fname

def write_table(fpath, header, rows, delim="\t"):
    outf = open(fpath, "w")
    outf.write(delim.join(map(str, header))+"\n")
    for row in rows:
        outf.write(delim.join(map(str, row))+"\n")
    outf.close()

def parse_prio_log(fpath, metrics):
    # run log is per project: run-hadoop-common.stdout
    data = []
    lines = [x.strip("\n") for x in open(fpath)]
    for line in lines:
        if line.startswith("[CPRIO]"):
            d = json.loads(line.strip("[CPRIO]"))
            scores = d["scores"].split(",")
            d["scores"] = {}
            for m, s in zip(metrics, scores):
                d["scores"][m] = float(s)
            data.append(d)
    return data


def sort_logs(logpaths):
    """fix the order of processing log from each model"""
    ret = []
    for m in ALLAPPS:
        for path in logpaths:
            if m in path:
                ret.append(path)
                break
    return ret

########################### extract per run / proj data from prioritization log

class resultLogParser:
    def __init__(self, log_dir, nrun, tcp_group, metrics):
        self.log_dir = log_dir # directory of prioritization log, i.e. ../logs
        self.nrun = nrun  # number of runs in the logs, same as `../pinput.py`
        self.tcp_group = tcp_group # techniques ran in the logs, add it to tcp_groups.py if non-exist
        self.metrics = metrics # list of metrics, i.e. [M_APMDC, M_APMD]

    def gen_perrun_data(self):
        """output: for each tcp: project, run, score (avg over files)"""
        print("\n>>>> generating perrun data")
        groupname, grouptcps = self.tcp_group
        metric_rows = {m:[] for m in self.metrics}
        logpaths = glob.glob(os.path.join(self.log_dir, "*.log"))
        for fpath in sort_logs(logpaths):
            print(">>>> parsing "+fpath)
            project = fpath.split("/")[-1].split(".")[0] # ../logs/hadoop-common.log
            assert project in ALLAPPS, "{} not in {}".format(project, " ".join(ALLAPPS))
            # load data
            data = parse_prio_log(fpath, self.metrics)
            print(">>>> processing %d (tcp, run, conf_chg) sample for %s"%(len(data), project))
            print(">>>> processing %d tcp for %s"%(len(data)/(NUM_MISCONF_FILES[project]*self.nrun), project))
            # build dictionary to run faster
            data_dict = {}
            for d in data:
                tcp = d["tcp"]
                run = d["run"]
                if tcp not in data_dict:
                    data_dict[tcp] = {}
                if run not in data_dict[tcp]:
                    data_dict[tcp][run] = {}
                data_dict[tcp][run][d["conf_chg"]] = d["scores"]
            # for each metric, get per seed averages over files
            for m in self.metrics:
                for run in [str(i) for i in range(self.nrun)]:
                    metric_row = [project, run]
                    for tcp in grouptcps:
                        scores = [v[m] for v in data_dict[tcp][run].values()] # d["scores"]
                        assert len(scores)==NUM_MISCONF_FILES[project], "wrong #conf_chg"
                        metric_row.append(statistics.mean(scores))
                    metric_rows[m].append(metric_row)
        # write data
        header = ["project", "run"]+grouptcps
        for m in self.metrics:
            write_table(PRIODATA_DIR+"/%s-perrun.tsv"%m, header, metric_rows[m])


    def gen_perproj_data(self):
        """output: for each tcp: project, tcp_score (avg over all runs and files)"""
        print("\n>>>> generating perproj data")
        groupname, grouptcps = self.tcp_group
        metric_rows = {m: [] for m in self.metrics}
        logpaths = glob.glob(os.path.join(self.log_dir, "*.log"))
        for fpath in sort_logs(logpaths):
            print(">>>> parsing "+fpath)
            project = fpath.split("/")[-1].split(".")[0] # ../logs/hadoop-common.log
            assert project in ALLAPPS, "{} not in {}".format(project, " ".join(ALLAPPS))
            # load data
            data = parse_prio_log(fpath, self.metrics)
            print(">>>> processing %d (tcp, run, file) sample for %s"%(len(data), project))
            print(">>>> processing %d files sample for %s"%(len(data)/(NUM_MISCONF_FILES[project]*self.nrun), project))

            # for each metric, get per project averages over files
            for m in self.metrics:
                metric_row = [project]
                for tcp in grouptcps:
                    scores = [d["scores"][m] for d in data if d["project"]==project and d["tcp"]==tcp]
                    assert len(scores)==NUM_MISCONF_FILES[project]*self.nrun, "wrong #conf_chg * #run"
                    metric_row.append(statistics.mean(scores))
                metric_rows[m].append(metric_row)
        # write results
        header = ["project"]+grouptcps
        for m in self.metrics:
            write_table(PRIODATA_DIR+"/%s-perproj.tsv"%m, header, metric_rows[m])


def gen_hsd_data(datafile, hsdfile, tcp_group, metric):
    groupname, grouptcps = tcp_group
    print("\n>>>> generating hsd for tcp group {} on metric {}".format(groupname, metric))
    dp = dataProcesser(tcp_group=tcp_group)
    # collect hsd
    dp.set_infpath(datafile%metric)
    dp.set_outfpath(hsdfile%(metric, groupname))
    dp.run_tukeyHSD_R()
    # use hsd
    fpath = hsdfile%(metric, groupname)
    lines = [x.strip("\n").split("\t") for x in open(fpath)][1:]
    data = {}
    for line in lines:
        tcp, avg, group = line
        data[tcp] = group.upper()
    return data


########################### data processor for parsing per run/sys data

class dataProcesser:
    def __init__(self, tcp_group, infpath=None, outfpath=None):
        self.tcp_group = tcp_group # tcp group (groupname, [tcp1, tcp2, ...]) in tcp_groups.py
        self.infpath = infpath # data path in prioData
        self.outfpath = outfpath # hsd output path

    def set_outfpath(self, outfpath):
        self.outfpath = outfpath

    def set_infpath(self, infpath):
        self.infpath = infpath

    def set_tcp_group(self, tcp_group):
        self.tcp_group = tcp_group

    def run_tukeyHSD_R(self):
        # convert raw data to format for R linear regression and tukey HSD
        tcp_scores = self.collect_tcp_scores()
        rows = []
        for tcp in tcp_scores:
            for score in tcp_scores[tcp]["tcp_score"]:
                rows.append([tcp, score])
        fdir, fname = dir_and_name(self.infpath)
        write_table(HSDDATA_DIR+"/R-"+fname, ["tcp", "score"], rows)
        # run tukeyHSD in R
        os.system("Rscript tukey.R {}/R-{} {}".format(HSDDATA_DIR, fname, self.outfpath))
        os.system("rm "+HSDDATA_DIR+"/R-"+fname)

    def collect_tcp_scores(self):
        # tcp_name: a list of scores, one score per file
        data = {}
        rows = [x.strip("\n").split("\t") for x in open(self.infpath)]
        for row in rows:
            if row[0].startswith("project"):
                for col, tcp in enumerate(row):
                    if tcp in set(self.tcp_group[1]):
                        data[tcp] = {"tcp_score": [], "tcp_column": col}
            else:
                for tcp in data.keys():
                    tcp_col = data[tcp]["tcp_column"]
                    tcp_score = float(row[tcp_col])
                    data[tcp]["tcp_score"].append(tcp_score)
        assert data != {}, "read tcp scores unsuccessful, data is empty!"
        return data


# Example: python3 preprocess.py --logdir=../logs --nrun=100 --metric=APMDc,APMD --group=alltcp
arg_parser = argparse.ArgumentParser("Extract data from output logs from ../main.py")
arg_parser.add_argument(
    "--logdir", type=str,
    help="Directory which stores the output logs.")
arg_parser.add_argument(
    "--tcps", type=str,
    help="Set of TCP techniques executed.")
arg_parser.add_argument(
    "--nrun", type=int,
    help="Number of times ran per TCP technique per configuration change.")
arg_parser.add_argument(
    "--metric", type=str,
    help="Metrics used, seperated by comma.")


def main():
    """extract data from prioritization logs"""
    args = arg_parser.parse_args()
    log_dir = args.logdir
    nrun = args.nrun
    groupname = args.tcps
    metric = args.metric
    
    if None in [log_dir, nrun, groupname, metric]:
        exit("Mandatory input is not provided, type `python3 preprocess.py -h` for help.")

    tcp_group = tcp_groups.groups[groupname]
    metrics = metric.strip().split(",")

    log_parser = resultLogParser(log_dir, nrun, tcp_group, metrics)
    log_parser.gen_perrun_data()
    log_parser.gen_perproj_data()
    for metric in metrics:
        datafile = PRIODATA_DIR+"/%s-perrun.tsv"
        hsdfile = HSDDATA_DIR+"/%s-perrun-%s.tsv"
        gen_hsd_data(datafile, hsdfile, tcp_group, metric)


if __name__ == '__main__':
    main()