import sys

from constant import *

"""
The file contain groups of test case prioritization (TCP) techniques 
that will be run and whose data will be processed.

The following groups are already defined:
- alltcp: all the tcps technique in the paper
- np (nonpeer): all non peer base tcp
- np_div (nonpeer_div): all non peer divided by time hybrid tcp
- np_bt (nonpeer_bt): all non peer break tie by time hybrid tcp
- p (peer): all peer-based base tcp
- p_div (peer_div): all peer-based divided by time hybrid tcp
- p_bt (peer_bt): all peer-based break tie by time hybrid tcp
- final: tcps for the final table in the paper

* For the meaning of each TCP variable name, see constant.py

You can add a new group of TCPs as follows:
1. define your group: your_group = ("YOUR_GROUP", [...])
2. add your group to the dictionary `groups` at the bottom of the file
"""


# your_group = ("YOUR_GROUP", [...])


alltcp =("alltcp", [
    # non peer base
    RANDOMIZED,
    QTF,
    T_CC_S, A_CC_S,
    T_CC_M, A_CC_M,
    T_PC, A_PC,
    T_PCC, A_PCC,
    T_ST_M, A_ST_M,
    T_STC_M, A_STC_M,
    IR_TEST_HIGH, IR_TEST_LOW,

    # non_peer divided by time hybrid
    RANDOMIZED_DIV,
    QTF_DIV,
    T_CC_M_DIV, A_CC_M_DIV,
    T_CC_S_DIV, A_CC_S_DIV,
    T_PC_DIV, A_PC_DIV,
    T_PCC_DIV, A_PCC_DIV,
    T_ST_M_DIV, A_ST_M_DIV,
    T_STC_M_DIV, A_STC_M_DIV,
    IR_TEST_LOW_DIV, IR_TEST_HIGH_DIV,

    # non_peer break ties by time hybrid
    RANDOMIZED_BT, 
    QTF_BT,
    T_CC_M_BT, A_CC_M_BT,
    T_CC_S_BT, A_CC_S_BT,
    T_PC_BT, A_PC_BT,
    T_PCC_BT, A_PCC_BT,
    T_ST_M_BT, A_ST_M_BT,
    T_STC_M_BT, A_STC_M_BT,
    IR_TEST_LOW_BT, IR_TEST_HIGH_BT,

    # peer based
    T_PF_ALL, A_PF_ALL,
    T_PF_DP, A_PF_DP,
    T_PF_PC, A_PF_PC,
    T_PF_RC, A_PF_RC,
    T_PF_PCC, 
    A_PF_PCC,
    T_PF_RCC, 
    A_PF_RCC,

    # peer based divided by time hybrid
    T_PF_ALL_DIV, A_PF_ALL_DIV,
    T_PF_DP_DIV, A_PF_DP_DIV,
    T_PF_PC_DIV, A_PF_PC_DIV,
    T_PF_RC_DIV, A_PF_RC_DIV,
    T_PF_PCC_DIV, A_PF_PCC_DIV,
    T_PF_RCC_DIV, A_PF_RCC_DIV,

    # peer based break ties by time hybrid
    T_PF_ALL_BT, A_PF_ALL_BT,
    T_PF_DP_BT, A_PF_DP_BT,
    T_PF_PC_BT, A_PF_PC_BT,
    T_PF_RC_BT, A_PF_RC_BT,
    T_PF_PCC_BT, A_PF_PCC_BT,
    T_PF_RCC_BT, A_PF_RCC_BT,
    ])

nonpeer = ("nonpeer", [
    # non peer base
    RANDOMIZED,
    QTF,
    T_CC_S, A_CC_S,
    T_CC_M, A_CC_M,
    T_PC, A_PC,
    T_PCC, A_PCC,
    T_ST_M, A_ST_M,
    T_STC_M, A_STC_M,
    IR_TEST_HIGH, IR_TEST_LOW,
    ])

nonpeer_div = ("nonpeer_div", [
    # non_peer divided by time hybrid
    RANDOMIZED_DIV,
    QTF_DIV,
    T_CC_M_DIV, A_CC_M_DIV,
    T_CC_S_DIV, A_CC_S_DIV,
    T_PC_DIV, A_PC_DIV,
    T_PCC_DIV, A_PCC_DIV,
    T_ST_M_DIV, A_ST_M_DIV,
    T_STC_M_DIV, A_STC_M_DIV,
    IR_TEST_LOW_DIV, IR_TEST_HIGH_DIV,
    ])

nonpeer_bt = ("nonpeer_bt", [
    # non_peer break ties by time hybrid
    RANDOMIZED_BT, 
    QTF_BT,
    T_CC_M_BT, A_CC_M_BT,
    T_CC_S_BT, A_CC_S_BT,
    T_PC_BT, A_PC_BT,
    T_PCC_BT, A_PCC_BT,
    T_ST_M_BT, A_ST_M_BT,
    T_STC_M_BT, A_STC_M_BT,
    IR_TEST_LOW_BT, IR_TEST_HIGH_BT,
    ])

peer = ("peer", [
    # peer based
    T_PF_ALL, A_PF_ALL,
    T_PF_DP, A_PF_DP,
    T_PF_PC, A_PF_PC,
    T_PF_RC, A_PF_RC,
    T_PF_PCC, 
    A_PF_PCC,
    T_PF_RCC, 
    A_PF_RCC,
    ])


peer_div = ("peer_div", [
    # peer based divided by time hybrid
    T_PF_ALL_DIV, A_PF_ALL_DIV,
    T_PF_DP_DIV, A_PF_DP_DIV,
    T_PF_PC_DIV, A_PF_PC_DIV,
    T_PF_RC_DIV, A_PF_RC_DIV,
    T_PF_PCC_DIV, A_PF_PCC_DIV,
    T_PF_RCC_DIV, A_PF_RCC_DIV,
    ])

peer_bt = ("peer_bt", [
    # peer based break ties by time hybrid
    T_PF_ALL_BT, A_PF_ALL_BT,
    T_PF_DP_BT, A_PF_DP_BT,
    T_PF_PC_BT, A_PF_PC_BT,
    T_PF_RC_BT, A_PF_RC_BT,
    T_PF_PCC_BT, A_PF_PCC_BT,
    T_PF_RCC_BT, A_PF_RCC_BT,
    ])


final = ("final", [
    RANDOMIZED,
    QTF,
    A_ST_M,
    A_CC_M_DIV,
    A_PF_PCC,
    A_PF_PCC_BT,
    ])

fast = ("fast", [RANDOMIZED, QTF])

groups = {
    "alltcp": alltcp,
    "nonpeer": nonpeer,
    "nonpeer_div": nonpeer_div,
    "nonpeer_bt": nonpeer_bt,
    "peer": peer,
    "peer_div": peer_div,
    "peer_bt": peer_bt,
    "final": final,
    "fast": fast, # intro example
    # "YOUR_GROUP": your_group,
}