# simulate prio techniques on ctest dataset
import time
import multiprocessing as mp

import ordering, parsing_utils, peer, utils
from constant import *
from pinput import *
from metric import Metric

TCPS = pinput["tcps"][1]


def load_prio_data(tcp):
    if tcp in [RANDOMIZED]:
        return {}
    elif tcp in [T_CC_M, A_CC_M]:
        return parsing_utils.code_coverage("method")
    elif tcp in [T_CC_S, A_CC_S]:
        return parsing_utils.code_coverage("stmt")
    elif tcp in [T_PC, A_PC]:
        return parsing_utils.param_coverage(change_aware=False)
    elif tcp in [T_PCC, A_PCC]:
        return parsing_utils.param_coverage(change_aware=True)
    elif tcp in [T_ST_M, A_ST_M]:
        return parsing_utils.config_trace_coverage(change_aware=False)
    elif tcp in [T_STC_M, A_STC_M]:
        return parsing_utils.config_trace_coverage(change_aware=True)
    elif tcp == QTF:
        return parsing_utils.default_runtime()
    elif tcp == IR_TEST_LOW:
        return parsing_utils.ir_model("test", LOW)
    elif tcp == IR_TEST_HIGH:
        return parsing_utils.ir_model("test", HIGH)
    elif tcp in [T_PF_ALL, A_PF_ALL]:
        return peer.pf_all()
    elif tcp in [T_PF_DP, A_PF_DP]:
        return peer.pf_dp()
    elif tcp in [T_PF_PC, A_PF_PC]:
        return peer.pf_pc()
    elif tcp in [T_PF_RC, A_PF_RC]:
        return peer.pf_rc()
    elif tcp in [T_PF_PCC, A_PF_PCC]:
        return peer.pf_pcc()
    elif tcp in [T_PF_RCC, A_PF_RCC]:
        return peer.pf_rcc()

    # hybrid
    data = {"d1": {}, "d2": {}, "d3": {}}
    if tcp in [T_CC_M_DIV, A_CC_M_DIV, T_CC_M_BT, A_CC_M_BT]:
        data["d1"] = parsing_utils.code_coverage("method")
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_CC_S_DIV, A_CC_S_DIV, T_CC_S_BT, A_CC_S_BT]:
        data["d1"] = parsing_utils.code_coverage("stmt")
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PC_DIV, A_PC_DIV, T_PC_BT, A_PC_BT]:
        data["d1"] = parsing_utils.param_coverage(change_aware=False)
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PCC_DIV, A_PCC_DIV, T_PCC_BT, A_PCC_BT]:
        data["d1"] = parsing_utils.param_coverage(change_aware=True)
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_ST_M_DIV, A_ST_M_DIV, T_ST_M_BT, A_ST_M_BT]:
        data["d1"] = parsing_utils.config_trace_coverage(change_aware=False)
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_STC_M_DIV, A_STC_M_DIV, T_STC_M_BT, A_STC_M_BT]:
        data["d1"] = parsing_utils.config_trace_coverage(change_aware=True)
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [IR_TEST_LOW_DIV, IR_TEST_LOW_BT]:
        data["d1"] = parsing_utils.ir_model("test", LOW)
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [IR_TEST_HIGH_DIV, IR_TEST_HIGH_BT]:
        data["d1"] = parsing_utils.ir_model("test", HIGH)
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [RANDOMIZED_DIV, QTF_DIV, RANDOMIZED_BT, QTF_BT]:
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PF_ALL_DIV, A_PF_ALL_DIV, T_PF_ALL_BT, A_PF_ALL_BT]:
        data["d1"] = peer.pf_all()
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PF_DP_DIV, A_PF_DP_DIV, T_PF_DP_BT, A_PF_DP_BT]:
        data["d1"] = peer.pf_dp()
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PF_PC_DIV, A_PF_PC_DIV, T_PF_PC_BT, A_PF_PC_BT]:
        data["d1"] = peer.pf_pc()
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PF_RC_DIV, A_PF_RC_DIV, T_PF_RC_BT, A_PF_RC_BT]:
        data["d1"] = peer.pf_rc()
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PF_PCC_DIV, A_PF_PCC_DIV, T_PF_PCC_BT, A_PF_PCC_BT]:
        data["d1"] = peer.pf_pcc()
        data["d2"] = parsing_utils.default_runtime()
    elif tcp in [T_PF_RCC_DIV, A_PF_RCC_DIV, T_PF_RCC_BT, A_PF_RCC_BT]:
        data["d1"] = peer.pf_rcc()
        data["d2"] = parsing_utils.default_runtime()
    else:
        exit("load_prio_data: unknown tcp: {}".format(tcp))
    return data


def prioritize(imgname, tcp, testinfo):
    # imgname: file name of the test result
    prio_data = load_prio_data(tcp)
    prio = ordering.Prio(tcp, imgname, testinfo, prio_data)
    if not tcp.endswith("_div") and not tcp.endswith("_bt"):
        # basic
        if tcp.startswith("add"):
            prio.additional()
        elif tcp.startswith("tot"):
            prio.total()
        elif tcp.startswith("randomized"):
            prio.randomized()
        elif tcp.startswith("qtf"):
            prio.qtf()
        elif tcp.startswith("ir"):
            prio.ir()
        else:
            exit("prioritize: unknown basic tcp: {}".format(tcp))
    else:
        # hybrid
        if tcp.startswith("add"):
            prio.additional_hybrid()
        elif tcp.startswith("tot"):
            prio.total_hybrid()
        elif tcp in [IR_TEST_LOW_DIV, IR_TEST_HIGH_DIV, IR_TEST_LOW_BT, IR_TEST_HIGH_BT]:
            prio.ir_hybrid()
        elif tcp in [RANDOMIZED_DIV, RANDOMIZED_BT]:
            prio.randomized_hybrid()
        elif tcp in [QTF_DIV, QTF_BT]:
            prio.qtf_hybrid()
        else:
            exit("prioritize: unknown hybrid tcp: {}".format(tcp))


def main():
    s = time.time()
    dataset = parsing_utils.parse_docker_dataset()
    pool = mp.Pool(max(1, mp.cpu_count()-2))
    mp_ret = pool.starmap(run_tcp, [(tcp, dataset) for tcp in TCPS])
    pool.close()
    logging.info("total-time: {}".format(time.time()-s))


def run_tcp(tcp, dataset):
    data_for_tcp = load_prio_data(tcp)
    for img, fdata in dataset.items():
        prioritize(img, tcp, fdata["testinfo"])

if __name__ == '__main__':
    main()