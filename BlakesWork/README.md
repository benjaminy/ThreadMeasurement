You'll need python3 and pyyaml (see http://pyyaml.org/wiki/PyYAMLDocumentation). Try 
```
sudo apt-get install python3-yaml
```

## To Collect Data:
On Linux, use the tool trace-cmd. This is a command-line interface for ftrace. To collect your data, Simply type 
```
sudo trace-cmd record -e sched
```
into your terminal. This will start collecting data. Perform your experiment and then go back to your terminal and press Ctrl+C to stop collecting data.
This will result in a file called "trace.dat" in your current working directory. The tool kernelshark is a good way to see the contents of this .dat file. 
You can enter the following in the terminal.
```
kernelshark trace.dat
```
On Windows7 (this might work for other versions of Windows too) run ETLgen.bat as an administrator. This will create a file called "log.csv" and potentially several numbered "log.etl" files. 
The csv contains your raw data. You can open the etl files with Windows Performance Analyzer for a visualization of the data similar to kernelshark. 

## To Analize the Data:
#### Converting from dat to csv
The first step here is to use dat_to_csv.py to convert the dat file into a more usable csv format. You can simply type 
```
./dat_to_csv.py filename.dat
```
into the terminal where "filename.dat" is the name of your dat file (including the path from dat_to_csv.py). This will result in a csv file with the same name in the same directory. If, for some reason, you want a different name for your csv, you can pass in the desired output file name and path as a second parameter. For example:
```
./dat_to_csv.py ../data/filename.dat ../data/othername.csv
```
The csv file will have column headers:

PID, Name, Start Time, Duration, IPID, APID.

IPID is the "internal process ID". There is a unique IPID for every (PID, Name) combination in the data. 

APID is the "Active period ID". Every active period has a unique APID.
#### Generating histograms
Use histograms.py to generate histograms that show which threads had the most active periods and which threads had the most time in your data. The histograms simply print to the terminal (thinking of changing this). Here's an example of how to run it:
```
./histograms.py pathtodata/mydata.csv
```
The first one shows the thread name, hown many active periods it had, and the cumulative percentage of active periods from the top of the histogram down including that thread. Here's an portion of an example:
```
	soffice.bin,7.361757,62.02635204
    Xorg,3.291399,89.7579755  
    gdbus,0.303831,92.31789816 
    lxpanel,0.184489,93.87230693 
    trace-cmd,0.138661,95.04059271 
    pcmanfm,0.085485,95.76084505 
    ibus-daemon,0.080335,96.43770616 
    openbox,0.071927,97.04372581 
    kworker/u8:0,0.033742,97.32801843
    ibus-ui-gtk3,0.033322,97.60877234
```
The second one shows the thread name, hown much active time it had, and the cumulative percentage of active time from the top of the histogram down including that thread. Here's an portion of an example:
```
	Xorg,11035,30.86713287
    soffice.bin,10840,61.18881119
    gdbus,3282,70.36923077
    trace-cmd,2175,76.45314685
    ibus-daemon,1624,80.9958042
    openbox,1213,84.38881119
    rcu\_sched,1013,87.22237762
    lxpanel,941,89.85454545
    ibus-ui-gtk3,349,90.83076923
    pcmanfm,330,91.75384615
```
#### Making a graph and getting some stats
Use csv_to_graphs.py to generate a nice graph from your data showing cumulative percentage of active periods and cumulative percentage of active time versus active period duration. Note that here we use the word "graph" colloquially.
```
./csv_to_graphs.py pathtodata/mydata.csv
```

If you have "save_graph" set to False under csv_to_graph in config.yml, it will simply display the graph. If "save_graph" is True, the graph will be saved in the same directory as the data from which it was generated as "mydata_graph.png" where "mydata" is the name of the csv. 

csv_to_graphs.py aslo provides some statistics like the total runtime, the total active time, the maximum, mean, and median active period durations, and 5 different overlap metrics in an attempt to quantify concurrency. If you have "save_info" set to True in config.yml, then this information will be appended to a csv file called "info.csv" in the same directory as your csv data.

## Scheduler simulators
sim2.py simulates how real data would have been different with a thread scheduler that, when an active period starts on one CPU core, briefly blocks other active periods from starting on the other cores. This block would persist until either the blocking active period ends or yields, or it runs for longer than the maximum block time. Because most active periods tend to be short, we hope that many of them can finish before the maximum block time elapses, thus allowing the next queueing active period to start without the possibility of creating concurrency issues with the first. 

We also propose the possibility of keeping track of threads that ran longer than the block time during their last active period, and not blocking when they become active again. This is sim3.py.

When running either of these from the command line, pass in first the path to the real csv data and then the block time as shown below:
```
./sim2.py ../data/mydata.csv 0.00015
```
This will result in a file called "mydata_sim.csv", where "mydata" is the name of your original csv data file, in the same directory as your original data. It will have the exact same format as the files generated by dat_to_csv.py. If you write your own scheduler simulators and want to use sim_graphs.py to evaluate them, you must follow these conventions. Make sure that the APIDs correspond to the original active periods in the real data. You must also have a function called sim(block_time, original_csv_data_file). 

## Evaluating scheduler simulators
sim_graphs.py will help you evaluate scheduler simulators. You specify which simulator and the other specifics of the evaluation in config.yml (see below). It will generate 3 graphs that show the scheduler's impact on runtime, responsiveness, and concurrency. Ideally, concurrency would decrease with little impact to runtime and responsiveness. Run it as shown:
```
./sim_graphs.py ../data/mydata.csv
```
If you want to evaluate your own scheduler simulation, make sure you followed the conventions above and import it at the top of sim_graphs.py. This is the only time you should have to edit something other than config.yml. 

## config.yml
Unless you are changing/adding functionality, you should only ever need to edit config.yml (unless you write your own scheduler and need to import it. See above). Here's an overview of your options. 
### sim_graphs
min_delay is the minimum block time with which the scheduler simulator will be tested. 

max_delay is the maximum block time with which the scheduler simulator will be tested. 

num_points is the number of different block times to tests on the simulator. These will be evenly distributed between min_delay and max_delay.

simulator is the name of the python file (without .py) that is the scheduler simulator you wish to evaluate.

save is a boolean that determines whether to save or display the 3 resulting graphs. (True for save, False for display).

### overlaps
how_long_is_long determines the definition of a "long" active period for purposes of counting pairwise overlap time not including long active periods and time with any overlap not including long active periods. Any active periods longer than (or equal to) this will be defined as long when calculating those statistics.

### sims
num_processors is the number of processors you want the simulated computer to have when simulating my scheduler modifications with sim2.py and sim3.py. If you write your own scheduler simulation, you can choose whether to include this value. Note that it does not have to be the same as the number of processors you used when collecting your data. It does need to be a positive integer. 

### csv_to_graphs
save_graph is a boolean that determines whether the graph gets saved or displayed.

save_info is a boolean that determines whether the statistics get appended to info.csv or only printed to the terminal.
