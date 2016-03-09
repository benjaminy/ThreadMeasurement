#!/usr/bin/env python3

''' This takes a csv file as produced by dat_to_csv.py and 
generates a new csv file that shows what the data would look like 
with a delay implemented in the kernel. The float 'delay' specifies how long
to block new threads for on startup. This simulation keeps track of IPIDs that
ran longer than the block time on their last active period and doesnt block for those.'''

import sys, operator, csv, yaml

def main():

    try:
        infile = sys.argv[1]
        delay = float(sys.argv[2])
    except:
        print ('Use the input csv file name as the first parameter and the delay length as the second.')
        exit(1)

    sim(delay, infile)

def sim (delay, infile):
    config = yaml.safe_load(open('config.yml'))
    num_procs = int(config['sims']['num_processors'])   
    longs = {}

    try:
        f = open(infile, 'r')
    except:
        print('File not found:  '+infile)
        exit(1)

    outfile = infile.split('.csv')[0] + '_sim.csv'

    actives = []

    for line in f:
        line_list = line.split(',')
        if line_list[0] == 'PID':
            continue
        line_list[5] = int(line_list[5])
        actives.append(line_list)

    time = float(actives[0][2])
    block = 0.0
    procs = [0.0] * num_procs
    block_proc = 100
    outs = []
    threads_delayed = 0
    delay_time = []
    start_time = float(actives[0][2])
    orig_end_time = 0.0
    new_end_time = 0.0
    for line in actives:
        if (float(line[2]) + float(line[3]) > orig_end_time):
            orig_end_time = float(line[2]) + float(line[3])
        # elapse time
        dur = float(line[2]) - time
        time += dur
        block -= dur
        if block < 0.0:
            block = 0.0
        for i in range(len( procs )):
            procs[i] -= dur
            if procs[i] < 0.0:
                procs[i] = 0.0
        if (not block_proc == 100) and procs[block_proc] == 0.0:
            block = 0.0        

        #start if can start
        if block == 0.0 and 0.0 in procs:
            proc = procs.index(0.0)   
            procs[proc] = float(line[3])
            if line[4] not in longs:
                block = delay
                block_proc = proc
            line[2] = time
            outs.append(line)
            if (float(line[2]) + float(line[3]) > new_end_time):
                new_end_time = float(line[2]) + float(line[3])
        
        #else elapse more time 
        else:
            dur = min(block, procs[block_proc])
            delay_time.append(dur)
            threads_delayed += 1
            time += dur
            block -= dur
            if block < 0.0:
                block = 0.0
            for i in range(len( procs )):
                procs[i] -= dur
                if procs[i] < 0.0:
                    procs[i] = 0.0
            if (not block_proc == -100) and procs[block_proc] == 0.0:
                block = 0.0  
            
            if 0.0 not in procs:
                dur = min(procs)
                delay_time.append(dur)
                time += dur
                block -= dur
                if block < 0.0:
                    block = 0.0
                for i in range(len( procs )):
                    procs[i] -= dur
                    if procs[i] < 0.0:
                        procs[i] = 0.0
                if (not block_proc == -100) and procs[block_proc] == 0.0:
                    block = 0.0  

            #start
            proc = procs.index(0.0)
            procs[proc] = float(line[3])
            if line[4] not in longs:
                block = delay
                block_proc = proc
            line[2] = time
            outs.append(line)
            if (float(line[2]) + float(line[3]) > new_end_time):
                new_end_time = float(line[2]) + float(line[3])

        if float(line[3]) > delay and not line[4] in longs:
            longs[line[4]] = line[4]
        if float(line[3]) <= delay and line[4] in longs:
            longs.pop(line[4])

    print(len(outs))
    print(str(sum(delay_time)) + '   delay_time')
    print(str(threads_delayed) + '   active_periods_delayed')
    if not threads_delayed == 0:
        print(sum(delay_time) / float(threads_delayed))
    print(str(new_end_time - orig_end_time) + '   Time difference')
    print('\n')
    output(outs, outfile)
    if len(delay_time) == 0:
        return 0.0
    else:
        return float(sum(delay_time)) / float(len(delay_time))


def output(outdata, outfile):
    outf = open(outfile, 'w')
    a = csv.writer(outf, delimiter=',')
    headers = ['PID', 'Name', 'Start Time', 'Duration', 'IPID', 'APID']
    a.writerow(headers)
    for elem in outdata:
        a.writerow(elem)


if __name__ == '__main__':
    main()








