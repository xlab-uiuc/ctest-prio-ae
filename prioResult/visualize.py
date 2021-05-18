import os, statistics, sys, re

from preprocess import *
import marcos
sys.path.insert(1, "..")
from constant import *
import tcp_groups

os.makedirs("figures", exist_ok=True)

mode = sys.argv[1]
if mode == "reproduce":
    PERPROJ_FILE = PRIODATA_DIR+"/release/%s-perproj-open.tsv"
    PERRUN_FILE = PRIODATA_DIR+"/release/%s-perrun-open.tsv"
elif mode == "rerun":
    PERPROJ_FILE = PRIODATA_DIR+"/%s-perproj.tsv"
    PERRUN_FILE = PRIODATA_DIR+"/%s-perrun.tsv"
else:
    exit("unknown mode")
PRERUN_HSDFILE = HSDDATA_DIR+"/%s-perrun-%s.tsv" # metric, groupname


def check_file_valdity():
    # check whether the data is enough to invoke the plotting functions
    try:
        for m in [M_APMDC, M_APMD]:
            projfile = [x.strip("\n").split("\t") for x in open(PERPROJ_FILE%m)]
            runfile = [x.strip("\n").split("\t") for x in open(PERRUN_FILE%m)]
            assert os.path.isfile(PERPROJ_FILE%m) and os.path.isfile(PERRUN_FILE%m), "file not found in prioData"
            assert len(runfile) == 501 and len(runfile[0]) == len(tcp_groups.alltcp[1])+2, "perrun file does not have enough data"
            assert len(projfile) == 6 and len(projfile[0]) == len(tcp_groups.alltcp[1])+1, "perproj file does not have enough data"
    except Exception as e:
        print(e)
        exit("Sorry, visualize.py can only plot data with the same experiment setup (100 runs, all techniques, on all projects) in the paper")
check_file_valdity()


############################ utils

def pad_zero_to_float(elem):
    try:
        float(elem)
        if elem[0] == '1':
            return elem.ljust(4, '0')
        else:
            return elem.ljust(5, '0')
        return True
    except Exception as e:
        return elem

def is_float(elem):
    try:
        float(elem)
        return True
    except Exception as e:
        return False

def format_rows(rows):
    for i, row in enumerate(rows):
        # round to 3 after decimal
        row = [round(n, 3) if is_float(n) else n for n in row]
        # convert row to str
        row = [str(n) for n in row]
        # pad 0 to the end
        row = [pad_zero_to_float(n) for n in row]
        # remove 0
        row = [re.sub(r'0\.', '.', n) for n in row]
        # replace with marcos
        rows[i] = [marcos.MARCOS[n] if n in marcos.MARCOS else n for n in row]
    return rows


############################### tables

def basic_base_table():
    # basic data, for RQ1

    # load data
    dp = dataProcesser(tcp_group=tcp_groups.nonpeer)
    dp.set_infpath(PERPROJ_FILE%M_APMDC)
    apmdc_data = dp.collect_tcp_scores()
    dp.set_infpath(PERPROJ_FILE%M_APMD)
    apmd_data = dp.collect_tcp_scores()
    # hsd
    apmdc_hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.nonpeer, M_APMDC)
    apmd_hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.nonpeer, M_APMD)

    # aggregate data
    merged = [] # row_i: hcommon_apmdc, hcommon_apmd, hdfs_apmdc, hdfs_apmd...
    for tcp in apmdc_data.keys():
        apmdc_scores = apmdc_data[tcp]["tcp_score"]
        apmd_scores = apmd_data[tcp]["tcp_score"]
        row = [tcp]
        for apmdc, apmd in zip(apmdc_scores, apmd_scores):
            row.append(apmdc)
            row.append(apmd)
        row.append(statistics.mean(apmdc_scores))
        row.append(statistics.mean(apmd_scores))
        row.append(apmdc_hsd[tcp])
        row.append(apmd_hsd[tcp])
        merged.append(row)

    # formatting and printing
    merged.sort(key=lambda x: (round(x[-4], 3), round(x[-3], 3)), reverse=True)
    format_rows(merged)
    print("\n")
    print("Table for RQ1: Basic, non-hybrid")
    print("TCP\t"+"\t\t".join(ALLAPPS_AB)+"\t\tAverage\t\tGroup")
    print("\t"+"\t".join(["APMDc\tAPMD"]*7))
    for row in merged:
        print("\t".join(row))


def basic_hybrid_table():
    # basic div and bt time comp, for RQ2
    
    # load div data
    dp = dataProcesser(tcp_group=tcp_groups.nonpeer_div)
    dp.set_infpath(PERPROJ_FILE%M_APMDC)
    div_data = dp.collect_tcp_scores()
    div_hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.nonpeer_div, M_APMDC)
    
    # load bt data
    dp.set_tcp_group(tcp_group=tcp_groups.nonpeer_bt)
    bt_data = dp.collect_tcp_scores()
    bt_hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.nonpeer_bt, M_APMDC)
    
    # aggregate data
    merged = [] # row_i: hcommon_div, hcommon_bt, hdfs_div, hdfs_bt...
    for tcp_div in div_data.keys():
        tcp_base = re.sub(r'_div', '', tcp_div)
        tcp_bt = tcp_base+"_bt"
        div_scores = div_data[tcp_div]["tcp_score"]
        bt_scores = bt_data[tcp_bt]["tcp_score"]
        row = [tcp_base]
        row.append(statistics.mean(div_scores))
        row.append(statistics.mean(bt_scores))
        row.append(div_hsd[tcp_div])
        row.append(bt_hsd[tcp_bt])
        merged.append(row)

    # formatting and printing
    merged.sort(key=lambda x: (round(x[-4], 3), round(x[-3], 3)), reverse=True)
    format_rows(merged)
    print("\n")
    print("Table for RQ2: Basic, hybrid")
    print("TCP\tAverage\t\tGroup")
    print("\t"+"\t".join(["Div.\tBt."]*2))
    for row in merged:
        print("\t".join(row))


def peer_table():
    # peer basic, div and bt time comp, for RQ3-1

    groupname, grouptcps = tcp_groups.peer
    dp = dataProcesser(tcp_group=tcp_groups.peer)
    dp.set_infpath(PERPROJ_FILE%M_APMDC)
    basic_data = dp.collect_tcp_scores()
    basic_hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.peer, M_APMDC)
    
    # load div data
    dp = dataProcesser(tcp_group=tcp_groups.peer_div)
    dp.set_infpath(PERPROJ_FILE%M_APMDC)
    div_data = dp.collect_tcp_scores()
    div_hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.peer_div, M_APMDC)
    
    # load bt data
    dp.set_tcp_group(tcp_group=tcp_groups.peer_bt)
    bt_data = dp.collect_tcp_scores()
    bt_hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.peer_bt, M_APMDC)
    
    # aggregate data
    merged = [] # row_i: hcommon_div, hcommon_bt, hdfs_div, hdfs_bt...
    for tcp in basic_data.keys():
        tcp_bt = tcp+"_bt"
        tcp_div = tcp+"_div"
        basic_scores = basic_data[tcp]["tcp_score"]
        div_scores = div_data[tcp_div]["tcp_score"]
        bt_scores = bt_data[tcp_bt]["tcp_score"]
        row = [tcp]
        row.append(statistics.mean(basic_scores))
        row.append(statistics.mean(div_scores))
        row.append(statistics.mean(bt_scores))
        row.append(basic_hsd[tcp])
        row.append(div_hsd[tcp_div])
        row.append(bt_hsd[tcp_bt])
        merged.append(row)

    # formatting and printing
    merged.sort(key=lambda x: (round(x[-6], 3), round(x[-5], 3)), reverse=True)
    format_rows(merged)
    print("\n")
    print("Table for RQ3-1: Peer-based, all")
    print("TCP\tAverage\t\t\tGroup")
    print("\t"+"\t".join(["Basic\tDiv.\tBt."]*2))
    for row in merged:
        print("\t".join(row))


def final_table():
    # compare the best tcps
    # load div data
    dp = dataProcesser(tcp_group=tcp_groups.final)
    dp.set_infpath(PERPROJ_FILE%M_APMDC)
    data = dp.collect_tcp_scores()
    hsd = gen_hsd_data(PERRUN_FILE, PRERUN_HSDFILE, tcp_groups.final, M_APMDC)

    # aggregate data
    merged = [] # row_i: hcommon, hdfs...
    for tcp in data.keys():
        scores = data[tcp]["tcp_score"]
        row = [tcp]+scores+[statistics.mean(scores), hsd[tcp]]
        merged.append(row)

    # formatting and printing
    merged.sort(key=lambda x: x[-2], reverse=True)
    format_rows(merged)
    print("\n")
    print("Table for RQ3-2: Summary")
    print("TCP\t"+"\t".join(ALLAPPS_AB)+"\tAverage\tGroup")
    for row in merged:
        print("\t".join(row))



########################## figures

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

APMDC_COLOR = "cornflowerblue"
APMDC_MEAN_COLOR = "springgreen"
APMD_COLOR = "pink"
APMD_MEAN_COLOR = "yellow"
DIV_COLOR = "mediumseagreen"
DIV_MEAN_COLOR = "yellow"
BT_COLOR = "orange"
BT_MEAN_COLOR = "cyan"

def basic_base_figure():
    dp = dataProcesser(tcp_group=tcp_groups.nonpeer)
    dp.set_infpath(PERRUN_FILE%M_APMD)
    apmd_data = dp.collect_tcp_scores()
    dp.set_infpath(PERRUN_FILE%M_APMDC)
    apmdc_data = dp.collect_tcp_scores()

    apmdc = [] # tcp_name, tcp_scores
    for tcp in apmdc_data.keys():
        scores = apmdc_data[tcp]["tcp_score"]
        row = [tcp, scores, statistics.mean(scores)]
        apmdc.append(row)
    apmdc.sort(key=lambda x: x[-1], reverse=True)

    apmd = {} # tcp_name, tcp_scores
    for tcp in apmd_data.keys():
        scores = apmd_data[tcp]["tcp_score"]
        apmd[tcp] = [scores, statistics.mean(scores)]

    handles = [
    mpatches.Patch(color=APMDC_COLOR), mpatches.Patch(color=APMD_COLOR),
    mpatches.Patch(color=APMDC_MEAN_COLOR), mpatches.Patch(color=APMD_MEAN_COLOR)#col 2
    ]
    labels = ["", "", M_APMDC, M_APMD]
    draw_comparison(
        data1=apmdc, data2=apmd, 
        violincolor1=APMDC_COLOR, violincolor2=APMD_COLOR, 
        meancolor1=APMDC_MEAN_COLOR, meancolor2=APMD_MEAN_COLOR,
        outfpath="figures/RQ1.pdf",
        xlabel="Non-Peer-Based TCP Techniques", ylabel="APMDc and APMD", 
        legend_items=[handles, labels, "lower left"],
        yticks_start=2)


def basic_hybrid_figure():
    dp = dataProcesser(tcp_group=tcp_groups.nonpeer_div)
    dp.set_infpath(PERRUN_FILE%M_APMDC)
    div_data = dp.collect_tcp_scores()
    
    # load bt data
    dp.set_tcp_group(tcp_group=tcp_groups.nonpeer_bt)
    bt_data = dp.collect_tcp_scores()

    div = [] # tcp_name, tcp_scores
    for tcp in div_data.keys():
        scores = div_data[tcp]["tcp_score"]
        tcp_base = re.sub(r'_div', '', tcp)
        row = [tcp_base, scores, statistics.mean(scores)]
        div.append(row)
    div.sort(key=lambda x: x[-1], reverse=True)

    bt = {} # tcp_name, tcp_scores
    for tcp in bt_data.keys():
        scores = bt_data[tcp]["tcp_score"]
        tcp_base = re.sub(r'_bt', '', tcp)
        bt[tcp_base] = [scores, statistics.mean(scores)]

    handles = [
    mpatches.Patch(color=DIV_COLOR), mpatches.Patch(color=BT_COLOR),
    mpatches.Patch(color=DIV_MEAN_COLOR), mpatches.Patch(color=BT_MEAN_COLOR)#col 2
    ]
    labels = ["", "", "Div", "Bt"]

    draw_comparison(
        data1=div, data2=bt, 
        violincolor1=DIV_COLOR, violincolor2=BT_COLOR, 
        meancolor1=DIV_MEAN_COLOR, meancolor2=BT_MEAN_COLOR,
        outfpath="figures/RQ2.pdf",
        xlabel="Hybrid Non-Peer-Based TCP Techniques", ylabel="APMDc", 
        legend_items=[handles, labels, "lower left"],
        yticks_start=2)


def draw_comparison(data1, data2, violincolor1, violincolor2, meancolor1, meancolor2, 
    outfpath, xlabel, ylabel, legend_items, yticks_start=0):

    # draw plot
    matplotlib.rcParams.update({"font.size": 18})
    matplotlib.rcParams.update({"figure.autolayout": True})
    fig, ax0 = plt.subplots()
    fig.set_figheight(5)
    fig.set_figwidth(23)
    # Adding a Grid below the plots
    ax0.yaxis.grid(True, linestyle="-", which="major", color="lightgrey",
               alpha=0.5)
    ax0.set_axisbelow(True)
    # Setting the axis lables
    ax0.set_ylabel(ylabel)

    labels = [marcos.TCP_MARCONAMES[x[0]] for x in data1]
    # positions
    ticks = [x for x in range(0, len(labels)*2, 2)] # 0, 2, 4, ...
    data1_pos = [x-0.4 for x in ticks]
    data2_pos = [x+0.4 for x in ticks]

    # plot violin
    data1_violin = plt.violinplot([x[1] for x in data1],
        positions=data1_pos,
        points=500,
        widths=0.6,
        showextrema=False,
        )
    data2_violin = plt.violinplot([data2[x[0]][0] for x in data1],
        positions=data2_pos,
        points=500,
        widths=0.6,
        showextrema=False,
        )

    # plot box
    box_color="#616161"
    data1_box = plt.boxplot(x=[x[1] for x in data1],
        patch_artist=True,
        positions=data1_pos,
        widths=0.07,
        showcaps=False,
        sym="",
        whiskerprops=dict(color=box_color),
        boxprops=dict(facecolor=box_color, edgecolor=box_color),
        medianprops=dict(linewidth=1.5, color='white'),
        zorder=1,)
    data2_box = plt.boxplot(x=[data2[x[0]][0] for x in data1],
        patch_artist=True,
        positions=data2_pos,
        widths=0.07,
        showcaps=False,
        sym="",
        whiskerprops=dict(color=box_color),
        boxprops=dict(facecolor=box_color, edgecolor=box_color),
        medianprops=dict(linewidth=1.5, color='white'),
        zorder=1,)

    # plot mean
    data1_dot = plt.plot(
        data1_pos, [x[2] for x in data1],
        linestyle="", marker="o", 
        markersize=7, markeredgecolor=meancolor1, markerfacecolor=meancolor1)
    data2_dot = plt.plot(
        data2_pos, [data2[x[0]][1] for x in data1],
        linestyle="", marker="o", 
        markersize=7, markeredgecolor=meancolor2, markerfacecolor=meancolor2)

    # set violine body color
    for patch in data1_violin['bodies']:
        patch.set_facecolor(violincolor1)
        patch.set_alpha(1)
        patch.set_edgecolor(box_color)
        patch.set_linewidth(1)
    for patch in data2_violin['bodies']:
        patch.set_facecolor(violincolor2)
        patch.set_alpha(1)
        patch.set_edgecolor(box_color)
        patch.set_linewidth(1)

    ax0.legend(handles=legend_items[0], labels= legend_items[1],
        loc=legend_items[2], frameon=False, ncol=2,
        handletextpad=0.5, handlelength=1, columnspacing=-0.5, labelspacing=0.1)
    plt.xlim(min(data1_pos)-0.5, max(data2_pos)+0.5)
    plt.xticks(ticks, labels)
    plt.yticks([i/10.0 for i in range(yticks_start, 11)], fontsize=15)
    fig.tight_layout()
    fig.savefig(outfpath)
    plt.close()


def peer_figure():
    dp = dataProcesser(tcp_group=tcp_groups.peer)
    dp.set_infpath(PERRUN_FILE%M_APMDC)
    basic_data = dp.collect_tcp_scores()

    dp = dataProcesser(tcp_group=tcp_groups.peer_div)
    dp.set_infpath(PERRUN_FILE%M_APMDC)
    div_data = dp.collect_tcp_scores()
    
    # load bt data
    dp.set_tcp_group(tcp_group=tcp_groups.peer_bt)
    bt_data = dp.collect_tcp_scores()

    base = [] # tcp_name, tcp_scores
    for tcp in basic_data.keys():
        scores = basic_data[tcp]["tcp_score"]
        row = [tcp, scores, statistics.mean(scores)]
        base.append(row)
    base.sort(key=lambda x: x[-1], reverse=True)

    div = {} # tcp_name, tcp_scores
    for tcp in div_data.keys():
        scores = div_data[tcp]["tcp_score"]
        tcp_base = re.sub(r'_div', '', tcp)
        div[tcp_base] = [scores, statistics.mean(scores)]

    bt = {} # tcp_name, tcp_scores
    for tcp in bt_data.keys():
        scores = bt_data[tcp]["tcp_score"]
        tcp_base = re.sub(r'_bt', '', tcp)
        bt[tcp_base] = [scores, statistics.mean(scores)]

    vc1 = "darkseagreen"
    vc2 = "skyblue"
    vc3 = "lavenderblush"
    mc1 = "lime"
    mc2 = "yellow"
    mc3 = "red"

    handles = [
    mpatches.Patch(color=vc1), mpatches.Patch(color=vc2), mpatches.Patch(color=vc3),
    mpatches.Patch(color=mc1), mpatches.Patch(color=mc2), mpatches.Patch(color=mc3)
    ]
    labels = ["", "", "", "Basic", "Div", "Bt"]

    draw_threeViolin(
        data1=base, data2=div, data3=bt, 
        violincolor1=vc1, violincolor2=vc2, violincolor3=vc3, 
        meancolor1=mc1, meancolor2=mc2, meancolor3=mc3,
        outfpath="figures/RQ3.pdf",
        xlabel="Hybrid Peer-Based TCP Techniques", ylabel="APMDc", 
        legend_items=[handles, labels, "lower left"],
        yticks_start=6)

def draw_threeViolin(data1, data2, data3,
    violincolor1, violincolor2, violincolor3,
    meancolor1, meancolor2, meancolor3,
    outfpath, xlabel, ylabel, legend_items, yticks_start=0):

    # draw plot
    matplotlib.rcParams.update({"font.size": 18})
    matplotlib.rcParams.update({"font.size": 18})
    matplotlib.rcParams.update({"figure.autolayout": True})
    fig, ax0 = plt.subplots()
    fig.set_figheight(5)
    fig.set_figwidth(20)
    # Adding a Grid below the plots
    ax0.yaxis.grid(True, linestyle="-", which="major", color="lightgrey",
               alpha=0.5)
    ax0.xaxis.grid(True, linestyle="-", which="major", color="lightgrey",
               alpha=0.5)
    ax0.set_axisbelow(True)
    # Setting the axis lables
    ax0.set_ylabel(ylabel)

    labels = [marcos.TCP_MARCONAMES[x[0]] for x in data1]
    # positions
    ticks = [x for x in range(0, len(labels)*3, 3)] # 0, 2, 4, ...
    data1_pos = [x-0.8 for x in ticks]
    data2_pos = [x for x in ticks]
    data3_pos = [x+0.8 for x in ticks]

    datapoints1 = [x[1] for x in data1]
    datapoints2 = [data2[x[0]][0] for x in data1]
    datapoints3 = [data3[x[0]][0] for x in data1]

    # plot violin
    data1_violin = plt.violinplot(datapoints1,
        positions=data1_pos,
        points=500,
        widths=0.6,
        showextrema=False,
        )
    data2_violin = plt.violinplot(datapoints2,
        positions=data2_pos,
        points=500,
        widths=0.6,
        showextrema=False,
        )
    data3_violin = plt.violinplot(datapoints3,
        positions=data3_pos,
        points=500,
        widths=0.6,
        showextrema=False,
        )

    # plot box
    box_color="#616161"
    data1_box = plt.boxplot(x=datapoints1,
        patch_artist=True,
        positions=data1_pos,
        widths=0.07,
        showcaps=False,
        sym="",
        whiskerprops=dict(color=box_color),
        boxprops=dict(facecolor=box_color, edgecolor=box_color),
        medianprops=dict(linewidth=1.5, color='white'),
        zorder=1,)
    data2_box = plt.boxplot(x=datapoints2,
        patch_artist=True,
        positions=data2_pos,
        widths=0.07,
        showcaps=False,
        sym="",
        whiskerprops=dict(color=box_color),
        boxprops=dict(facecolor=box_color, edgecolor=box_color),
        medianprops=dict(linewidth=1.5, color='white'),
        zorder=1,)
    data3_box = plt.boxplot(x=datapoints3,
        patch_artist=True,
        positions=data3_pos,
        widths=0.07,
        showcaps=False,
        sym="",
        whiskerprops=dict(color=box_color),
        boxprops=dict(facecolor=box_color, edgecolor=box_color),
        medianprops=dict(linewidth=1.5, color='white'),
        zorder=1,)

    # plot mean
    data1_dot = plt.plot(
        data1_pos, [x[2] for x in data1],
        linestyle="", marker="o", 
        markersize=7, markeredgecolor=meancolor1, markerfacecolor=meancolor1)
    data2_dot = plt.plot(
        data2_pos, [data2[x[0]][1] for x in data1],
        linestyle="", marker="o", 
        markersize=7, markeredgecolor=meancolor2, markerfacecolor=meancolor2)
    data3_dot = plt.plot(
        data3_pos, [data3[x[0]][1] for x in data1],
        linestyle="", marker="o", 
        markersize=7, markeredgecolor=meancolor3, markerfacecolor=meancolor3)

    # set violine body color
    for patch in data1_violin['bodies']:
        patch.set_facecolor(violincolor1)
        patch.set_alpha(1)
        patch.set_edgecolor(box_color)
        patch.set_linewidth(1)
    for patch in data2_violin['bodies']:
        patch.set_facecolor(violincolor2)
        patch.set_alpha(1)
        patch.set_edgecolor(box_color)
        patch.set_linewidth(1)
    for patch in data3_violin['bodies']:
        patch.set_facecolor(violincolor3)
        patch.set_alpha(1)
        patch.set_edgecolor(box_color)
        patch.set_linewidth(1)
    ax0.legend(handles=legend_items[0], labels= legend_items[1],
        loc=legend_items[2], frameon=False, ncol=2,
        handletextpad=0.5, handlelength=1, columnspacing=-0.5, labelspacing=0.1)
    plt.xlim(min(data1_pos)-0.5, max(data3_pos)+0.5)
    plt.xticks(ticks, labels)
    plt.yticks([0.65]+[i/10.0 for i in range(yticks_start+1, 11)], fontsize=15)
    fig.tight_layout()
    fig.savefig(outfpath)
    plt.close()


def gen_tables():
    basic_base_table()
    basic_hybrid_table()
    peer_table()
    final_table()

def get_figures():
    basic_base_figure()
    basic_hybrid_figure()
    peer_figure()

if __name__ == '__main__':
    gen_tables()
    get_figures()