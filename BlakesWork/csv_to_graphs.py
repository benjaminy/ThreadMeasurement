#!/usr/bin/env python3

''' This generates some graphs from the csv data output by dat_to_csv.py '''

import sys, os, csv, yaml
import matplotlib.pyplot as plt
from overlaps import count_overlaps, pairwise_overlap_time, pairwise_time_sans_longs, time_any_overlaps, any_overlaps_sans_longs
config = yaml.safe_load(open('config.yml')) 
save_info = bool(config['csv_to_graphs']['save_info'])
save_graph = bool(config['csv_to_graphs']['save_graph'])

def main():
    infile = 'trace.csv'
    if (len(sys.argv) == 2):
        infile = sys.argv[1]
    f = open(infile, 'r')
    
    data = []
    end_time = -1.0
    for line in f:
        line = line.split(',')
        if line[0] == 'PID':
            continue
        end = float(line[2]) + float(line[3])
        if  end > end_time:
            end_time = end
        data.append(line)
    f.close()
    
    data.sort( key = lambda x: float(x[2]))

    events = len(data)
    start_time = float(data[0][2])
    runtime = end_time - start_time
    
    shortest_first = sorted(data, key = lambda x: float(x[3]), reverse = False)
    info = (stats(shortest_first))
    print_stats(info, infile)

    num_overlaps = count_overlaps(data)
    pairwise_overlaps = pairwise_overlap_time(data)
    posl = pairwise_time_sans_longs(data)
    any_overlaps = time_any_overlaps(data)
    any_sl = any_overlaps_sans_longs(data)

    print('Runtime:  '+ str(runtime))
    print('Active Periods:  ' + str(events))
    print (str(num_overlaps) + '% of active periods had some overlap')
    print (str(pairwise_overlaps) + '  Seconds of pairwise overlap time')
    print(str(posl) + '  Seconds of pairwise overlap time without long active periods')
    print (str(any_overlaps) + ' Seconds of any concurrency')
    print(str(any_sl) + '  Seconds of any overlap time without long active periods')

    if save_info:
        header = ['Name', 'Runtime', 'Active Periods', 'Active Time','Longest Active Period','Mean Active Period Length','Median Active Period Length','% of active periods had some overlap', 'Seconds of pairwise overlap', 'Seconds of pairwise overlap time without long active periods', 'Seconds of any concurrency', 'Seconds of any overlap time without long active periods']
        path, basename = os.path.split(infile)
        information = [basename, runtime, events]
        information += info
        information += [num_overlaps, pairwise_overlaps, posl, any_overlaps, any_sl]
        save(path+'/info.csv', header, information)

    xs, ys1 = graph1(shortest_first, info[0])
    ys2 = graph2(shortest_first, events)
    graph(xs, ys1, ys2, infile)
    
def save (filename, header, info):
    assert len(header) == len(info)
    if (not os.path.isfile(filename)) or (os.stat(filename).st_size == 0):
        outf = open(filename, 'w')
        a = csv.writer(outf, delimiter=',')
        a.writerow(header)
        a.writerow(info)
        outf.close()
    else:
        outf = open(filename, 'a')
        a = csv.writer(outf, delimiter=',')
        a.writerow(info)
        outf.close()

def stats (matrix) : 
    active_time = 0.0
    max_active = matrix[-1][3]
    median_active = matrix[int(len(matrix)/2)][3]
    for line in matrix:
        active_time += float(line[3])
    mean_active = active_time / float(len(matrix))
    return (active_time, max_active, mean_active, median_active)
    
def print_stats (tup, infile):
    print ('Active time:  ' + str(tup[0]))
    print('Longest active period:  '+ str(tup[1]))
    print('Mean active period length:  '+str(tup[2]))
    print('Median active period length:  '+str(tup[3]))

def graph (xs, ys1, ys2, infile):
    fig, ax1 = plt.subplots()
    ax1.plot(xs, ys2, 'b.')
    ax1.set_xlabel('Active Period Length (s)')
    ax1.set_ylabel('Cumulative Percentage of Active Periods', color = 'b')
    ax1.set_xscale('log')
    ax1.set_ylim([-0.05, 1.05])
    ax1.set_xlim([0.000001, 1.0])
    ax2 = ax1.twinx()
    ax2.plot(xs, ys1, 'r.')
    ax2.set_ylabel('Cumulative Percentage of Active Time', color = 'r')
    ax2.set_xscale('log')
    ax2.set_ylim([-0.05, 1.05])
    ax2.set_xlim([0.000001, 1.0])

    #print('\n\n')
    #print(ys1[int(len(ys1)*0.9)])
    #print(ys2[int(len(ys2)*0.9)])
    #print(xs[int(len(xs)*0.9)])

    if save_graph :
        plt.savefig(infile[0: -4]+'_graph.png')
    else:
        plt.show()

def graph1 (matrix, active_time) :
    xs = []
    ys = []
    cumtime = 0.0
    percent = 0.0
    for line in matrix:
        xs.append(float(line[3]))
        cumtime += float(line[3])
        percent = float(cumtime)/float(active_time)
        ys.append(percent)
    return (xs, ys)
    

def graph2 (matrix, active_threads) :
    ys = []
    num = 0
    percent = 0.0
    for line in matrix:
        num += 1
        percent = float(num)/float(active_threads)
        ys.append(percent)
    return ys

if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
