#!/usr/bin/env python3

'''This takes an input .dat file name and an output file name as parameters. 
If no output file name is supplied, it will have the same name as the .dat file except it will be .csv.
The input file is assumed to be in the Linux Ftrace .dat format. 
This program reads the input file and converts it into a csv format.'''

import sys, subprocess, tempfile, csv
import matplotlib.pyplot as plt

def main ():
    if len(sys.argv) <= 1 or len(sys.argv) > 3:
        print ('Please supply the .dat file name as the first parameter. You may supply the desired output file name as the second parameter if you wish.')
        exit(-1)

    if (len(sys.argv) == 3):
        infile = sys.argv[1]
        outfile = sys.argv[2]
    
    if (len(sys.argv) == 2):
        infile = sys.argv[1]
        outfile = infile[0:-4] + '.csv'
        
    txt_file = tempfile.NamedTemporaryFile(mode='w+b')
    dat_to_txt(infile, txt_file.name)
    
    data = []
    for line in txt_file:
        line = line.decode('utf-8')
        if 'sched_switch' in line:
            event = breakup(line)
            data.append(event)

    add_durations(data)
    data = trim(data)   
    data = remove_idles(data)
    give_ids(data)
    add_apids(data)
    collapse(data)
    save(data, outfile)

def add_apids (data):
    for i in range(len(data)):
        data[i].append(i)

def remove_idles (indata):
    idles = ['swapper/0', 'swapper/1', 'swapper/2', 'swapper/3']
    ret = []
    for line in indata:
        if (line[1] not in idles) and (not line[3] == 0.0):
            ret.append(line)
    return ret

def add_durations(data):
    for i in range(len(data)):
        data[i].append(get_duration(i,data))

def collapse (data):
    prev = {}
    max_int = 0.000001
    max_betweens = 2
    count = 0
    total = 0
    for line in data:
        total += 1
        ipid = line[4]
        if ipid not in prev:
            prev[ipid] = line
            continue
        interval = float(line[2]) - (float(prev[ipid][2]) + float(prev[ipid][3]))
        between = int(line[5]) - int(prev[ipid][5])
        prev[ipid] = line
        if interval <= max_int and between <= max_betweens:
            count += 1
    print(str(count) + ' / '+str(total))
    print(count/total)
        

def give_ids (data):
    table = {}
    current_id = 0
    for i in range(len(data)):
        tup = (data[i][0], data[i][1])
        if tup in table.keys():
            data[i].append(table[tup])
        else:
            table[tup] = current_id
            data[i].append(current_id)
            current_id += 1
            

def trim (data):
    ret = []
    for line in data:
        newline = []
        newline.append(line[3])
        newline.append(line[4])
        newline.append(line[6])
        newline.append(line[10])
        ret.append(newline)
    assert len(ret) == len(data)
    return ret

def get_duration(index, data):
    line = data[index]
    index += 1
    for i in range(index, len(data)):
        if int(line[5]) == int(data[i][5]):
            return float(data[i][6]) - float(line[6])
    return 0.0 #For the last thread on each processor because duration is unknown
    
def save (data, outfile):    
    outf = open(outfile, 'w')
    headers = ['PID', 'Name', 'Start Time', 'Duration', 'IPID', 'APID']
    
    a = csv.writer(outf, delimiter=',')
    a.writerow(headers)

    for line in data:
        a.writerow(line)
    
def breakup(linestr):
    
    line = linestr.split(' ')
    line = list(filter(None, line))
    towrite = ['Event Type', 'Old PID', 'Old Process Name', 'New PID', 'New Process Name', 'Processor', 'Time Stamp', 'Previous State', 'Old Priority', 'New Priority']
    
    # Sometimes there are spaces in the process names
    # We have a problem if there are '[' or ']' and spaces in a single process name
    # Also a problem if there is a process called 'sched_switch'
    if len(line) > len(towrite):
        halfs = linestr.split('==>')
        second = halfs[1].split(' ')
        second = list(filter(None, second))
        second = '_'.join(second)
        second = second.split('_[')
        second = ' ['.join(second)
        second = second.split(' ')
        first = halfs[0].split('sched_switch:')
        first0 = first[0].split(' ')
        first0 = list(filter(None, first0))
        first0 = '_'.join(first0)
        first0 = first0.split('_[')
        first0 = ' ['.join(first0)
        first0 = first0.split(']_')
        first0 = '] '.join(first0)
        first0 = first0.split(' ')        

        first1 = first[1].split(' ')
        first1 = list(filter(None, first1))
        first1 = '_'.join(first1)
        first1 = first1.split('_[')
        first1 = ' ['.join(first1)
        first1 = first1.split(']_')
        first1 = '] '.join(first1)
        first1 = first1.split(' ')
        first = first0 + ['sched_switch:'] + first1
        
        line = first + ['==>'] + second
 
    if not len(line) == len(towrite):
        print (line)
    assert len(line) == len(towrite)
        
    towrite[0] = line[3].rstrip(':')
    
    tup = line[4].split(':')
    # Apparently some process names also contain ':'
    towrite[2] = ':'.join(tup[0:-1])
    towrite[1] = tup[-1]
    tup = line[8].split(':')
    towrite[4] = ':'.join(tup[0:-1])
    towrite[3] = tup[-1]
    
    towrite[5] = int(line[1].strip('[]'))
    towrite[6] = line[2].rstrip(':')
    towrite[7] = line[6]
    towrite[8] = line[5].strip('[]')
    towrite[9] = line[9].strip('[]\n')
    return towrite

def dat_to_txt(in_name, out_name):
    try:
        cmd = ['trace-cmd report -i '+in_name+' > '+out_name]
        return_code = subprocess.call(cmd, shell=True)

        if return_code != 0:
            print (out_name)
            print ('Bad return code '+str(return_code))
            raise Exception()
    except:
        print ('Command failed')
        raise


if __name__ == '__main__':
    main()
