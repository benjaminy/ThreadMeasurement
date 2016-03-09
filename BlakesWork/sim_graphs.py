#!/usr/bin/env python3

''' Makes graphs to evaluate the changes to runtime, responsiveness, and concurrency for a scheduler simulator.'''

import sys, os, yaml, sim2, sim3
import matplotlib.pyplot as plt
from overlaps import count_overlaps, pairwise_overlap_time, pairwise_time_sans_longs, time_any_overlaps, any_overlaps_sans_longs

def main():
    assert(len(sys.argv) == 2)
    config = yaml.safe_load(open('config.yml'))
    tosave = bool(config['sim_graphs']['save'])
    points = int(config['sim_graphs']['num_points'])
    min_delay = float(config['sim_graphs']['min_delay'])
    max_delay = float(config['sim_graphs']['max_delay'])
    incr = (max_delay - min_delay) / float(points)
    cur = min_delay
    simulator = config['sim_graphs']['simulator']
    #sorry
    xs = []
    ys = []
    ys2 = []
    ys3 = []
    ys4 = []
    ys5 = []
    ys6 = []
    median_delay = []
    max_delay = []
    delay_90th = []
    percent_delayed = []
    name_prefix = sys.argv[1].split('.csv')[0]
    outfile = name_prefix + '_sim.csv'

    orig_data = []
    f = open(sys.argv[1], 'r')
    for line in f:
        line = line.split(',')
        if line[0] == 'PID':
            continue
        orig_data.append(line)
    f.close()

    for i in range(points+1):
        data = []
        xs.append(cur)
        eval(simulator + '.sim('+str(cur) + ', \'' + sys.argv[1]+'\')')
        f = open(outfile, 'r')
        end_time = -1.0
        active_time = 0.0
        start_time = float('inf')
        for line in f:
            line = line.split(',')
            if line[0] == 'PID':
                continue
            data.append(line)
            end = float(line[2]) + float(line[3])
            start = float(line[2])
            active_time += float(line[3])
            if  end > end_time:
                end_time = end
            if  start < start_time:
                start_time = start
        f.close()

        runtime = end_time - start_time
        ys.append(runtime)
        ys2.append(count_overlaps(data))
        ys3.append(pairwise_overlap_time(data))
        ys4.append(pairwise_time_sans_longs(data))
        ys5.append(time_any_overlaps(data))
        ys6.append(any_overlaps_sans_longs(data))
        dinfo = get_delay_stats(orig_data, data)
        percent_delayed.append(dinfo[0])
        median_delay.append(dinfo[1])
        max_delay.append(dinfo[2])
        delay_90th.append(dinfo[3])
        cur += incr

    # runtime graph
    fig, ax1 = plt.subplots()
    ax1.plot(xs, ys, 'b.')
    ax1.set_xlabel('Block Time (s)')
    ax1.set_ylabel('Runtime (s)', color = 'b')

    if tosave :
        plt.savefig(name_prefix + '_runtime.png')
    else:
        plt.show()

    # benefit graph
    fig, ax1 = plt.subplots()
    ax1.plot(xs, ys2, color = 'black', marker = '.', linestyle = '-.')
    ax1.set_xlabel('Block Time (s)')
    ax1.set_ylabel('% of Active Periods with Any Overlap (dashed line)')
    ax2 = ax1.twinx()
    ax2.plot(xs, ys3)
    ax2.plot(xs, ys4)
    ax2.plot(xs, ys5)
    ax2.plot(xs, ys6)
    ax2.set_ylabel('Seconds')
    lgd = ax2.legend(['Total Pairwise Overlap Time', 'Pairwise Overlap Time Without Long Active Periods', 'Time with Any Overlaps', 'Time with Any Overlaps Not Including Long Active Periods'], loc = 'upper center', bbox_to_anchor = (0.5, -0.12), fancybox = True, shadow = True, ncol = 1)
    fig.subplots_adjust(bottom = 0.3)

    if tosave :
        plt.savefig(name_prefix + '_benefit.png')
    else:
        plt.show()

    # responsiveness graph
    fig, ax1 = plt.subplots()
    ax1.plot(xs, percent_delayed, color = 'black', marker = '.', linestyle = '-.')
    ax1.set_xlabel('Block Time (s)')
    ax1.set_ylabel('% of Active Periods Delayed (dashed line)')
    ax2 = ax1.twinx()
    ax2.plot(xs, max_delay)
    ax2.plot(xs, delay_90th)
    ax2.plot(xs, median_delay)
    ax2.set_ylabel('Seconds')
    lgd = ax2.legend(['Longest Delay Time', '90th Percentile Delay Time', 'Median Delay Time'], loc = 'upper center', bbox_to_anchor = (0.5, -0.15), fancybox = True, shadow = True, ncol = 1)
    fig.subplots_adjust(bottom = 0.3)

    if tosave :
        plt.savefig(name_prefix + '_resp.png')
    else:
        plt.show()

def get_delay_stats(orig_data, new_data):
    assert len(orig_data) == len(new_data)
    orig_data.sort( key = lambda x: int(x[5]))
    new_data.sort( key = lambda x: int(x[5]))
    delays = []
    for i in range(len(orig_data)):
        if float(orig_data[i][2]) == float(new_data[i][2]):
            # this is where you would append 0.0 if you were so inclined
            continue
        elif float(orig_data[i][2]) < float(new_data[i][2]):
            delays.append(float(new_data[i][2]) - float(orig_data[i][2]))
        else:
            print('Things are starting before they were supposed to in your simulated data')
    delays.sort()
    if len(delays) == 0:
        return (0.0, 0.0, 0.0, 0.0)
    return (len(delays)/len(orig_data), delays[int(len(delays)/2)], delays[-1], delays[int(len(delays)*0.9)])
            

if __name__ == '__main__':
    main()





