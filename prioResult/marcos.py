import sys

sys.path.insert(1, "..")
from constant import *

MARCOS = {
	# module
	HCOMMON: "\\hcommon",
	HBASE: "\\hbase",
	HDFS: "\\hdfs",
	ZOOKEEPER: "\\zookeeper",
	ALLUXIO: "\\alluxio",

	# metric
	M_APMD: "\\apmd",
	M_APMDC: "\\apmdc",

	RANDOMIZED: "\\random",
	T_CC_M: "\\totCC",
	A_CC_M: "\\addCC",
	T_CC_S: "\\totCCS",
	A_CC_S: "\\addCCS",
	QTF: "\\qtf",
	T_PC: "\\totPC",
	A_PC: "\\addPC",
	T_PCC: "\\totPCChg",
	A_PCC: "\\addPCChg",
	T_ST_M: "\\totSTrace",
	A_ST_M: "\\addSTrace",
	T_STC_M: "\\totSTraceChg",
	A_STC_M: "\\addSTraceChg",
	IR_TEST_HIGH: "\\irHigh",
	IR_TEST_LOW: "\\irLow",


	# peer based
	T_PF_ALL: "\\totPeerFile",
	T_PF_RC: "\\totPeerRootCause",
	T_PF_DP: "\\totPeerChangedParam",
	T_PF_PC: "\\totPeerReadParam",
	A_PF_ALL: "\\addPeerFile",
	A_PF_RC: "\\addPeerRootCause",
	A_PF_DP: "\\addPeerChangedParam",
	A_PF_PC: "\\addPeerReadParam",
	T_PF_PCC: "\\totPeerReadParamCov",
	T_PF_RCC: "\\totPeerRootCauseCov",
	A_PF_PCC: "\\addPeerReadParamCov",
	A_PF_RCC: "\\addPeerRootCauseCov",

	# in final table
	A_CC_M_DIV: "\\addCC+\\divTime",
	A_PF_PCC_BT: "\\addPeerReadParamCov+\\btTime"
}


TCP_MARCONAMES = {

	# tcp
	RANDOMIZED: "Rand",
	T_CC_M: "CC$^{m}_{tot}$",
	A_CC_M: "CC$^{m}_{add}$",
	T_CC_S: "CC$^{s}_{tot}$",
	A_CC_S: "CC$^{s}_{add}$",
	QTF: "QTF",
	T_PC: "PC$_{tot}$",
	A_PC: "PC$_{add}$",
	T_PCC: "PC$^{D}_{tot}$",
	A_PCC: "PC$^{D}_{add}$",
	T_ST_M: "ST$_{tot}$",
	A_ST_M: "ST$_{add}$",
	T_STC_M: "ST$^{D}_{tot}$",
	A_STC_M: "ST$^{D}_{add}$",
	IR_TEST_HIGH: "IR$_{high}$",
	IR_TEST_LOW: "IR$_{low}$",


	# peer based
	T_PF_ALL: "Conf$^{ALL}_{tot}$",
	T_PF_RC: "Conf$^{RC}_{tot}$",
	T_PF_DP: "Conf$^{DP}_{tot}$",
	T_PF_PC: "Conf$^{PC}_{tot}$",
	A_PF_ALL: "Conf$^{ALL}_{add}$",
	A_PF_RC: "Conf$^{RC}_{add}$",
	A_PF_DP: "Conf$^{DP}_{add}$",
	A_PF_PC: "Conf$^{PC}_{add}$",
	T_PF_PCC: "Para$^{PC}_{tot}$",
	T_PF_RCC: "Para$^{RC}_{tot}$",
	A_PF_PCC: "Para$^{PC}_{add}$",
	A_PF_RCC: "Para$^{RC}_{add}$",
}

def gen_marco():
	for k, v in MARCOS.items():
		n = v.strip("\\")
		print("\\newcommand{\\%s}{\\it %s}"%(n, n))

if __name__ == '__main__':
	gen_marco()