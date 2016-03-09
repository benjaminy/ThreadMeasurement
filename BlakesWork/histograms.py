#!/usr/bin/env python3

''' This generates two sets of histogram data from the csv file of sched_switch events. 
The first set of data shows active periods per process, and the second shows time per process.
Change the integer disp to specify how many processes to output data for. (e.g. disp==10 means output data for the top 10 processes.)
a disp value < 0 will output data for all processes.'''

import sys, operator, linecache

def main():
    infile = 'trace.csv'
    if (len(sys.argv) == 2):
        infile = sys.argv[1]
    f = open(infile, 'r')

    hist1 = {}
    hist2 = {}
    runtime = 0.0
    events = 0

    for line in f:
        line_list = line.split(',')
        if line_list[0] == 'PID':
            continue
        name = line_list[1]
        pid = int(line_list[0])
        start_time = float(line_list[2])
        duration = float(line_list[3])
        ipid = int(line_list[4])
        if name not in hist1:
            hist1[name] = 1
            events += 1
        else:
            hist1[name] += 1
            events += 1
        if name not in hist2:
            hist2[name] = duration
            runtime += duration
        else:
            hist2[name] += duration
            runtime += duration
        
    assert len(hist1) == len(hist2)
    print('\n')
    output(hist1, events)
    print('\n')
    output(hist2, runtime)
    print('\n')
    print('Runtime:  '+ str(runtime))
    print('Events:  '+ str(events))
    print(len(hist1))

def output(hist, total):
    disp = -1
    cum_perc = 0.0
    x = sorted(hist.items(), key=operator.itemgetter(1), reverse=True)
    if disp < 0 or disp > len(x):
        disp = len(x)
    for i in range(disp):
        line = x[i]
        cum_perc += line[1] / total
        print (str(line[0]) + ',' + str(line[1]) + ','+ str(cum_perc * 100))



if __name__ == '__main__':
    main()
