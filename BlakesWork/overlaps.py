#!/usr/bin/env python3
import yaml

''' These are the functions for getting data regarding the overlaps from a list of active periods. '''

config = yaml.safe_load(open('config.yml'))
delay = float(config['overlaps']['how_long_is_long'])

def get_overlap_length (period1, period2) :
    ''' returns the overlap length of 2 active periods.
         Make sure that the first starts before the second. '''
    start1 = float(period1[2])
    start2 = float(period2[2])
    assert start1 <= start2
    start2 = start2 - start1    
    start1 = 0.0
    end1 = start1 + float(period1[3])
    end2 = start2 + float(period2[3])
    if start2 >= end1:
        return 0.0
    if end2 <= end1:
        return end2 - start2
    if end2 > end1:
        return end1 - start2
    print('something bad happened when counting overlap time')

def overlap_length_only_short (period1, period2) :
    ''' returns the overlap length of 2 active periods. 
        Returns 0 if either of the 2 periods is "long". 
        Make sure that the first starts before the second. '''
    if float(period1[3]) > delay or float(period2[3]) > delay:
        return 0.0
    else:
        return get_overlap_length(period1, period2)

def overlap_length_not_both_long (period1, period2, delay) :
    ''' returns the overlap length of 2 active periods. 
        Returns 0 if both of the 2 periods are "long". 
        Make sure that the first starts before the second. '''
    if float(period1[3]) > delay and float(period2[3]) > delay:
        return 0.0
    else:
        return get_overlap_length(period1, period2)

def count_overlaps (threads) :
    '''count number of threads that have any overlap
    if a thread overlaps with more than one other thread, count them all'''
    total_overlaps = 0
    did = {}
    for i in range(len(threads)):
        start = float(threads[i][2])
        end = float(threads[i][2]) + float(threads[i][3])
        next = False
        plus = 1
        while not next:
            if i+plus >= len(threads):
                next = True
                continue
            temp = float(threads[i+plus][2])
            if temp >= start and temp < end:
                if threads[i][5] not in did:
                    total_overlaps += 1
                    did[threads[i][5]] = threads[i][5]
                if threads[i+plus][5] not in did:
                    total_overlaps += 1
                    did[threads[i+plus][5]] = threads[i+plus][5]
                plus += 1
            elif temp >= end:
                next = True
            else:
                print (temp)
                print (start)
                print (end)
                print ("Something bad happened in count_overlaps \n")
    percent = (total_overlaps/len(threads))*100.0
    return percent

def pairwise_overlap_time (threads) :
    ''' Returns the total overlap time for the list of active periods.
        So 4 threads running concurrently for 1 second counts the same as 2 threads running concurrently for 2 seconds.''' 
    overlap_time = 0.0
    for i in range(len(threads)):
        start = float(threads[i][2])
        end = float(threads[i][2]) + float(threads[i][3])
        next = False
        plus = 1
        while not next:
            if i+plus >= len(threads):
                next = True
                continue
            temp = float(threads[i+plus][2])
            if temp >= start and temp < end:
                overlap_time += get_overlap_length(threads[i], threads[i+plus])
                plus += 1
            elif temp >= end:
                next = True
            else:
                print ("Something bad happened in pairwise_overlap_time")
    return overlap_time

def pairwise_time_sans_longs (threads) :
    ''' Returns the total overlap time for the list of active periods.
        So 4 threads running concurrently for 1 second counts the same as 2 threads running concurrently for 2 seconds.''' 
    overlap_time = 0.0
    for i in range(len(threads)):
        start = float(threads[i][2])
        end = float(threads[i][2]) + float(threads[i][3])
        next = False
        plus = 1
        while not next:
            if i+plus >= len(threads):
                next = True
                continue
            temp = float(threads[i+plus][2])
            if temp >= start and temp < end:
                overlap_time += overlap_length_only_short(threads[i], threads[i+plus])
                plus += 1
            elif temp >= end:
                next = True
            else:
                print ("Something bad happened in pairwise_time_sans_longs")
    return overlap_time

def time_any_overlaps (threads) :
    ''' Returns the time with any overlap at all. 
    So 3 threads running concurrently for 1 second counts the same as 2 threads running concurrently for 1 second.''' 
    running = []
    time = float(threads[0][2])
    overlap_time = 0.0
    for i in range(len(threads)):
        running.append(float(threads[i][3]))
        running.sort()
        while len(running) >= 1 and i<len(threads)-1 and running[0] < (float(threads[i+1][2]) - time):
            dur = running[0]
            time += dur
            if len(running) > 1:
                overlap_time += dur
            for j in range(len(running)):
                running[j] -= dur
            running[:] = (value for value in running if value > 0.0)
        if i<len(threads)-1:        
            dur = float(threads[i+1][2]) - time
            time += dur
            if len(running) > 1:
                overlap_time += min(running[-2], dur)
            for k in range(len(running)):
                running[k] -= dur
            running[:] = (value for value in running if value > 0.0)
        else:
            if len(running) > 1:
                overlap_time += running[-2]
    return overlap_time

# Works for many simple test cases. Not my finest algorithm. Wouldn't trust it with my life. Would probably trust it with $100 though. 
def any_overlaps_sans_longs (threads) :
    ''' Returns the time with any overlap at all. 
    So 3 threads running concurrently for 1 second counts the same as 2 threads running concurrently for 1 second.''' 
    running = []
    time = float(threads[0][2])
    overlap_time = 0.0
    for i in range(len(threads)-1):
        if float(threads[i][3]) > delay:
            continue
        running.append(float(threads[i][3]))
        running.sort()
        while len(running) >= 1 and running[0] < (float(threads[i+1][2]) - time):
            dur = running[0]
            time += dur
            if len(running) > 1:
                overlap_time += dur
            for j in range(len(running)):
                running[j] -= dur
            running[:] = (value for value in running if value > 0.0)
                
        dur = float(threads[i+1][2]) - time
        time += dur
        if len(running) > 1:
            overlap_time += min(running[-2], dur)
        for k in range(len(running)):
            running[k] -= dur
        running[:] = (value for value in running if value > 0.0)

    if float(threads[-1][3]) <= delay:
        running.append(float(threads[-1][3]))
        running.sort()
    if len(running) > 1:
        overlap_time += running[-2]
    return overlap_time






                
