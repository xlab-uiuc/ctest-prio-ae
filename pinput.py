import sys, os, logging, argparse
from constant import *
import tcp_groups

"""
- project: one of hadoop-common, hadoop-hdfs, alluxio-core, hbase-server, zookeeper-server
- metrics: M_APMDC, M_APMD, see constant.py
- nrun: number of times to run per technique per configuration change
- tcps: specific group of tcps to run, you can run pre-defined groups or create new groups, see tcp_groups.py for more
- logdir: directory to store the output logs, will be used by prioResult/preprocess.py
"""


arg_parser = argparse.ArgumentParser("Run TCP techniques on given project data")
arg_parser.add_argument(
    "--project", type=str,
    help="Project to run: alluxio-core, hadoop-common, hadoop-hdfs, hbase-server, or zookeeper-server.")
arg_parser.add_argument(
    "--tcps", type=str,
    help="Name of the set of TCP techniques to run. Need to define it if not exists in tcp_groups.py.")
arg_parser.add_argument(
    "--metric", default="APMDc,APMD", type=str, 
    help="Metrics used, seperated by comma. default: `APMDc,APMD`.")
arg_parser.add_argument(
    "--nrun", type=int,
    help="Number of times to run per TCP technique per configuration change.")
arg_parser.add_argument(
    "--logdir", type=str,
    help="Directory to store output log.")

args = arg_parser.parse_args()
project = args.project
nrun = args.nrun
metric = args.metric
tcps = args.tcps
logdir = args.logdir

if None in [project, nrun, metric, tcps, logdir]:
    exit("Mandatory input not provided. type `python3 main.py -h` for help.")


pinput = {
    "project": project,
    "metrics": metric.strip().split(","),
    "nrun": nrun,
    "tcps": tcp_groups.groups[tcps],
    "logdir": logdir,
}

# logging results
os.makedirs(logdir, exist_ok=True)
logging.basicConfig(filename=os.path.join(logdir, "%s.log"%project), filemode='w', 
    format='%(message)s', level=logging.DEBUG)

for k, v in pinput.items():
    if type(v) == type([]):
        v = "\t".join([str(x) for x in v])
    logging.info(">>>>{}: {}".format(k, v))
logging.StreamHandler().flush()

assert project in [HCOMMON, HDFS, HBASE, ALLUXIO, ZOOKEEPER], "module is not supported."
