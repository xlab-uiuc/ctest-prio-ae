import os

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
CTESTDATA_DIR = os.path.join(CUR_DIR, "ctestData")
TESTINFO_DIR = os.path.join(CUR_DIR, "testInfo")
CC_DIR = os.path.join(TESTINFO_DIR, "codeCoverage")
EXECTIME_DIR = os.path.join(TESTINFO_DIR, "execTime")
IRDOC_DIR = os.path.join(TESTINFO_DIR, "irDoc")
TRACE_DIR = os.path.join(TESTINFO_DIR, "stackTrace")


HCOMMON = "hadoop-common"
HDFS = "hadoop-hdfs"
HBASE = "hbase-server"
ALLUXIO = "alluxio-core"
ZOOKEEPER = "zookeeper-server"
ALLAPPS = [HCOMMON, HDFS, HBASE, ZOOKEEPER, ALLUXIO]
ALLAPPS_AB = ["HCommon", "HDFS", "HBase", "ZooKeeper", "Alluxio"]


M_SUBDIR = {
    HCOMMON: "hadoop-common-project/hadoop-common",
    HDFS: "hadoop-hdfs-project/hadoop-hdfs",
    HBASE: "hbase-server",
    ZOOKEEPER: "zookeeper-server",
    ALLUXIO: "core",
}

NUM_MISCONF_FILES = {
    HCOMMON: 20,
    HDFS: 16,
    HBASE: 12,
    ZOOKEEPER: 14,
    ALLUXIO: 4,
}

##### {} should be hadoop-common, hadoop-hdfs, etc

# CC
STMT_COVERAGE_FILE = os.path.join(CC_DIR, "{}/{}-stmt.json")
METHOD_COVERAGE_FILE = os.path.join(CC_DIR, "{}/{}-method.json")

# execution time
EXECTIME_FILE = os.path.join(EXECTIME_DIR, "{}/{}-testcase.tsv")

# stack trace
TRACE_FILE = os.path.join(TRACE_DIR, "{}/{}-method.json")

# IR
HIGH = "high"
LOW = "low" 


# Ctest dataset
CTEST_MAPPING = os.path.join(CTESTDATA_DIR, "ctestMapping/opensource-{}.json")
# new names of configuration parameter names that have been deprecated
DEPRECATE_CONF_MAP_FILE = os.path.join(CUR_DIR, "dmap.txt")
TESTRESULT_DIR = os.path.join(CTESTDATA_DIR, "testResult/{}")
TR_REGEX = r'test_result_(.*?)\.tsv'
TR_PATTERN = "test_result*tsv"
DOCKER_FILE_DIR = os.path.join(CTESTDATA_DIR, "dockerConf/{}")
FAILURE_MAP_DIR = os.path.join(CTESTDATA_DIR, "failureToMisconf/{}")
FM_REGEX = r'failed_test_result_(.*?)\.tsv'
C_FLAKY = "flaky"
C_HARDCODED = "hardcoded"
C_EFFECTIVE = "effective"

############### METRIC
M_APMD = "APMD"
M_APMDC = "APMDc"


############# PRIORITIZATION
RANDOMIZED = "randomized"

# code coverage, m: method, s: statement
T_CC_M = "tot_ccm"
A_CC_M = "add_ccm"
T_CC_S = "tot_ccs"
A_CC_S = "add_ccs"

QTF = "qtf"

# parameger coverage, sys: change-unaware, chg: change-aware
T_PC = "tot_pc-sys"
A_PC = "add_pc-sys"
T_PCC = "tot_pc-chg"
A_PCC = "add_pc-chg"

# context stack trace 
T_ST_M = "tot_st-sys"
A_ST_M = "add_st-sys"
T_STC_M = "tot_st-chg"
A_STC_M = "add_st-chg"

# IR
IR_TEST_HIGH = "ir_test_high"
IR_TEST_LOW = "ir_test_low"


# hybrid, divided by time
RANDOMIZED_DIV = "randomized_div"
QTF_DIV = "qtf_div"
T_CC_M_DIV = "tot_ccm_div"
A_CC_M_DIV = "add_ccm_div"
T_PC_DIV = "tot_pc-sys_div"
A_PC_DIV = "add_pc-sys_div"
T_PCC_DIV = "tot_pc-chg_div"
A_PCC_DIV = "add_pc-chg_div"
T_ST_M_DIV = "tot_st-sys_div"
A_ST_M_DIV = "add_st-sys_div"
T_STC_M_DIV = "tot_st-chg_div"
A_STC_M_DIV = "add_st-chg_div"
IR_TEST_LOW_DIV = "ir_test_low_div"
IR_TEST_HIGH_DIV = "ir_test_high_div"
T_CC_S_DIV = "tot_ccs_div"
A_CC_S_DIV = "add_ccs_div"

# hybrid, break tie by time
RANDOMIZED_BT = "randomized_bt"
QTF_BT = "qtf_bt"
T_CC_M_BT = "tot_ccm_bt"
A_CC_M_BT = "add_ccm_bt"
T_PC_BT = "tot_pc-sys_bt"
A_PC_BT = "add_pc-sys_bt"
T_PCC_BT = "tot_pc-chg_bt"
A_PCC_BT = "add_pc-chg_bt"
T_ST_M_BT = "tot_st-sys_bt"
A_ST_M_BT = "add_st-sys_bt"
T_STC_M_BT = "tot_st-chg_bt"
A_STC_M_BT = "add_st-chg_bt"
IR_TEST_LOW_BT = "ir_test_low_bt"
IR_TEST_HIGH_BT = "ir_test_high_bt"
T_CC_S_BT = "tot_ccs_bt"
A_CC_S_BT = "add_ccs_bt"


# peer based: pf
# all: Conf_ALL, rc: Conf_RC, dp: Conf_DP, pc: Conf_PC
# configuration granularity
T_PF_ALL = "tot_pf_all"
T_PF_RC = "tot_pf_rc"
T_PF_DP = "tot_pf_dp"
T_PF_PC = "tot_pf_pc"
A_PF_ALL = "add_pf_all"
A_PF_RC = "add_pf_rc"
A_PF_DP = "add_pf_dp"
A_PF_PC = "add_pf_pc"
# parameter granularity
T_PF_PCC = "tot_pf_pcc" 
T_PF_RCC = "tot_pf_rcc"
A_PF_PCC = "add_pf_pcc"
A_PF_RCC = "add_pf_rcc"

# peer based hybrid divided by time
T_PF_ALL_DIV = "tot_pf_all_div"
T_PF_RC_DIV = "tot_pf_rc_div"
T_PF_DP_DIV = "tot_pf_dp_div"
T_PF_PC_DIV = "tot_pf_pc_div"
A_PF_ALL_DIV = "add_pf_all_div"
A_PF_RC_DIV = "add_pf_rc_div"
A_PF_DP_DIV = "add_pf_dp_div"
A_PF_PC_DIV = "add_pf_pc_div"
T_PF_PCC_DIV = "tot_pf_pcc_div"
T_PF_RCC_DIV = "tot_pf_rcc_div"
A_PF_PCC_DIV = "add_pf_pcc_div"
A_PF_RCC_DIV = "add_pf_rcc_div"

# peer based hybrid break ties by time
T_PF_ALL_BT = "tot_pf_all_bt"
T_PF_RC_BT = "tot_pf_rc_bt"
T_PF_DP_BT = "tot_pf_dp_bt"
T_PF_PC_BT = "tot_pf_pc_bt"
A_PF_ALL_BT = "add_pf_all_bt"
A_PF_RC_BT = "add_pf_rc_bt"
A_PF_DP_BT = "add_pf_dp_bt"
A_PF_PC_BT = "add_pf_pc_bt"
T_PF_PCC_BT = "tot_pf_pcc_bt"
T_PF_RCC_BT = "tot_pf_rcc_bt"
A_PF_PCC_BT = "add_pf_pcc_bt"
A_PF_RCC_BT = "add_pf_rcc_bt"



IMG_DEPENDENT = set([
    T_PCC, A_PCC,
    T_STC_M, A_STC_M, 

    T_PCC_DIV, A_PCC_DIV,
    T_STC_M_DIV, A_STC_M_DIV,

    T_PCC_BT, A_PCC_BT,
    T_STC_M_BT, A_STC_M_BT,

    T_PF_ALL, A_PF_ALL,
    T_PF_DP, A_PF_DP,
    T_PF_PC, A_PF_PC,
    T_PF_RC, A_PF_RC,
    T_PF_PCC, A_PF_PCC,
    T_PF_RCC, A_PF_RCC,

    T_PF_ALL_DIV, A_PF_ALL_DIV,
    T_PF_DP_DIV, A_PF_DP_DIV,
    T_PF_PC_DIV, A_PF_PC_DIV,
    T_PF_RC_DIV, A_PF_RC_DIV,
    T_PF_PCC_DIV, A_PF_PCC_DIV,
    T_PF_RCC_DIV, A_PF_RCC_DIV,

    T_PF_ALL_BT, A_PF_ALL_BT,
    T_PF_DP_BT, A_PF_DP_BT,
    T_PF_PC_BT, A_PF_PC_BT,
    T_PF_RC_BT, A_PF_RC_BT,
    T_PF_PCC_BT, A_PF_PCC_BT,
    T_PF_RCC_BT, A_PF_RCC_BT,
    ])
