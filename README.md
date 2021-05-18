

# Research Artifact: Test-Case Prioritization for Configuration Testing

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4742567.svg)](https://doi.org/10.5281/zenodo.4742567)

This is the artifact of the research paper, "Test-Case Prioritization for Configuration Testing", at the ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA), 2021.


## About

Configuration changes are among the dominating causes of failures of large-scale software system deployment. Configuration testing is a technique that detects misconfigurations by testing configuration changes together with the code that uses the changed configurations. In the paper, we studied how to reorder configuration tests via various test-case prioritization (TCP) techniques to speed up detection of misconfigurations. 

This artifact contains experiment scripts and results from our study. We also provide a dataset for configuration testing and configuration test prioritization research. 

## Getting Started

### Requirements

- Languages: Python3, R >= 3.5.0.
- Libraries: gensim 3.8.3, matplotlib on Python3; agricolae on R.

### Setting Up with Docker

Docker is a popular lightweight virtualization tool, which you can use to run our artifact regardless of your local environment. See [official docs](https://docs.docker.com/get-docker/) for installing Docker.

After Docker started running:


```Bash
# build Docker image with requirements
docker build -t ctest_prio_art .
```

```Bash
# start a Docker container, mount ctest_prio_art/

# Linux and Mac users:
docker run -v $(pwd):/ctest_prio_art -it ctest_prio_art /bin/bash

# Windows users:
docker run -v "%cd%":/ctest_prio_art -it ctest_prio_art /bin/bash
```

```Bash
cd ctest_prio_art
```

### Decompressing Data Files

```Bash
# find and unzip data files
find . -name "*.zip" | while read filename; do unzip -o -d "`dirname "$filename"`" "$filename"; done
```

### A Quick Start

```Bash
# run randomized and QTF TCP 10 times on HDFS data
python3 main.py --project=hadoop-hdfs --tcps=fast --nrun=10 --metric=APMDc,APMD --logdir=logs
# takes ~30 seconds, output to logs/hadoop-hdfs.log

# process logs and generate HSD tables
cd prioResult
python3 preprocess.py --logdir=../logs --tcps=fast --nrun=10 --metric=APMDc,APMD
# output 4 data tables in prioData/ and 2 HSD tables in hsdTable/ for randomized and QTF TCP
```

- Output logs in `logs/` are the raw data including project stats, and outcome of each (config change, run, TCP) tuple.
- Better techniques have lexicographically smaller group letter(s) in HSD tables.

## Detailed Description: How to Use


### Reproducibility

You can reproduce tables and figures in the paper with our experiment results `prioResult/prioData/release/*-open.tsv`.


```Bash
cd prioResult

# generate tables and figures in the paper
python3 visualize.py reproduce
# takes ~20 seconds, output summary tables in stdout, 3 .pdf figures in figures/, and HSD tables as by-product in hsdTable/
```


### Rerunning Our Experiment

You can rerun the experiment in our paper.


```Bash
# $project can be alluxio-core, hadoop-common, hadoop-hdfs, hbase-server, or zookeeper-server
python3 main.py --project=$project --tcps=alltcp --nrun=100 --metric=APMDc,APMD --logdir=logs
# may take several hours per project

# collect output for all 5 projects (do it only after running all 5 projects)
cd prioResult
python3 preprocess.py --logdir=../logs --tcps=alltcp --nrun=100 --metric=APMDc,APMD

# generate tables and figures in the paper
python3 visualize.py rerun
```

- APMDc and APMD scores may not be exactly the same as the paper's due to the randomness in breaking ties in TCP techniques.
- Our experiments were run on Ubuntu 18.04 with 8-core Intel i7-9700 CPU with 32 GB memory. *This is only a reference, a machine with different specifications also works.* 

### Running More Experiments

You can also run more experiments on the current dataset.

1. Follow `tcp_groups.py` to define a new set of TCP techniques to experiment with.
2. You can set a different number of runs, TCP group, and logging directory. Run `python3 main.py -h` to see different options.


```Bash
# after editing tcp_groups.py
python3 main.py -h --project=$project --tcps=$tcps --nrun=$nrun --metric=$metric --logdir=$logdir

cd prioResult
python3 preprocess.py -h --logdir=../$logdir --tcps=$tcps --nrun=$nrun --metric=$metric
```

- Prior log of the same project in the same `$logdir` will be overwritten. Data in `prioResult/prioData` will also be overwritten automatically, except `prioResult/prioData/release/*.tsv`.
- If your new experiment data does not contain results of all TCPs on all projects (same as the experiment setting in the paper), you cannot use `visualize.py` to generate tables and figures in the paper. But you can still use `preprocess.py` to generate HSD tables.

## Dataset

### Overview

We include a dataset for future research in configuration test prioritization and configuration testing. It contains 66 failing configuration changes from 5 popular systems.

| System    | Version | #Changes | Avg #Params | Avg #Misconfs | Avg #Ctests |
|-----------|---------|----------|-------------|---------------|-------------|
| HCommon   | 2.8.5   | 20       | 3.75        | 1.05          | 955.75      |
| HDFS      | 2.8.5   | 16       | 5.19        | 1.31          | 1680.12     |
| HBase     | 2.2.2   | 12       | 8.33        | 1.92          | 1254.25     |
| ZooKeeper | 3.5.6   | 14       | 6.57        | 1.71          | 74.36       |
| Alluxio   | 2.1.0   | 4        | 13.75       | 1.25          | 949         |


### Layout

`ctestData/` organizes the dataset as several subdirectories:
- `dockerConf/`: 66 failing configuration changes, from [ctest](https://github.com/xlab-uiuc/openctest).
- `ctestMapping/`:  Configuration parameters and their ctests, from [ctest](https://github.com/xlab-uiuc/openctest).

- `testResult/`: Test results of these configuration changes: ctest name,  outcome (pass or fail), and test execution time reported by Maven Surefire.
- `failureToMisconf/`: Failed ctests, their failure types and root-cause misconfigured parameters. Failure type can be `effective`, `flaky`, or `hardcoded`. `effective`: Failure is caused by misconfiguration; `flaky`: failure is nondeterministic; `hardcoded`: failure is caused by hidden constraints in the test rather than misconfiguration. We consider that only `effective` ctests have detected misconfigurations.

### Test Information Data

We also include test information used to guide configuration test prioritization in our paper, organized in `testInfo/` as follows:

- `codeCoverage/`: Method- and statement-level code coverage collected using OpenClover 4.4.1. File names are encoded in `*-fileID.json`.  Coverage file format: each method maps to a list of elements (format: `fileID-$line number of method signature or statement`) it covers.

- `irDoc/`: Test file tokens extracted using JavaParser 3.17.0. `high` tokens come only from identifiers, `low` tokens also include comments, and string literals.
  - Format: Test classes map to their methods; methods map to their tokens. Classes also map to tokens in the test file but not inside any methods (`global`) and their superclasses (`extendedClasses`)

- `execTime/`: Test-method and test-class execution time under default configurations of 5 independent runs.

- `stackTrace/`: Method- and statement-level stacktrace coverage collected using [ctest](https://github.com/xlab-uiuc/openctest). Method names are encoded in `*-methodID.json`. Each ctest maps to their tested parameters; parameters map to methods (format: `methodID`) or statements (format: `methodID#$line number of executed statement in method`) invoked when ctest accesses the parameter.


## Contact

For questions about our paper or artifact, please contact [Sam Cheng](rcheng12@illinois.edu).
