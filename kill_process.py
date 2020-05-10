# This program is used to kill the process
# when system used memory is more than the threshold limit set.
# Update ProcessName and ProcessArgs to match with your process to kill

#!/usr/bin/env python

import psutil
import os
import signal
import subprocess
import logging
from datetime import datetime
from pytz import timezone

# Variables and thresholds
ProcessName = "sleep"
ProcessArgs = "10m"
usedMemoryThreshold = 35
totalFreeMemoryThreshold = 1024
processThreshold = 2
processKillSignal = "signal.SIGTERM"
localTimezone = "UTC"
processRunningTimeThreshold = 100
processMemoryThreshold = 0.3

# Find system memory details
def find_memory():
    total_memory = psutil.virtual_memory().total / (1024.0 ** 2)
    available_memory = psutil.virtual_memory().available / (1024.0 ** 2)
    free_memory = psutil.virtual_memory().free / (1024.0 ** 2)
    total_free_memory = available_memory + free_memory
    used_mem_per = psutil.virtual_memory().percent
    logger.info("------------------------------------------------")
    logger.info("MEMORY STATS")
    logger.info("Total Memory (MB): %s" % total_memory)
    logger.info("Total Free Memory (MB): %s" % total_free_memory)
    logger.info("Used Memory: %s" % used_mem_per)
    logger.info("------------------------------------------------")
    return used_mem_per

# Find the number of process identified
def shutting_worker_count():
    cmd = "pgrep -f -c '%s %s'" % (ProcessName, ProcessArgs)
    try:
        run = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.exception(e)
    process_shut_count = run.communicate()[0]
    logger.info("Total Process: %s" % process_shut_count)
    logger.info("------------------------------------------------")

# Get the list of process details
def findProcessIdByName(processName, processArgs):
    listOfProcessObjects = [] 
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'memory_percent', 'connections'])
            if processName in pinfo['name'] and processArgs in pinfo['cmdline']:
                no_of_connections = len(pinfo['connections'])
                pinfo['connections'] = no_of_connections
                listOfProcessObjects.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess, psutil.TimeoutExpired) as exception:
            logger.exception(exception)
            pass
    sortedlistOfProcess = sorted(listOfProcessObjects, key = lambda x: x['create_time'])
    print(sortedlistOfProcess)
    return sortedlistOfProcess 

def findLocaltime():
    format = "%Y-%m-%d %H:%M:%S"
    now_utc = datetime.now(timezone(localTimezone)).replace(tzinfo=None)
    return(now_utc)

# Determine which process to kill based on thresholds and send sigterm signal
def main():
    global logger
    logging.basicConfig(filename='/var/log/process_shutting_kill.log',format='%(asctime)s %(message)s')
    logger=logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    memory_used = find_memory()
    shutting_worker_count()
    local_time=findLocaltime()
    listOfProcessIds = findProcessIdByName(ProcessName, ProcessArgs)
    if len(listOfProcessIds) > 0 and memory_used > usedMemoryThreshold:
        logger.info("List of process running more than %d hours with current system memory >> %d%%" % (processRunningTimeThreshold,usedMemoryThreshold))
        logger.info("PID\tPROCESS NAME\tSTART TIME\t\t\tEND TIME\t\tRUNNING(Hrs)\tPROCESS MEMORY(%)\tTOTAL CONNECTIONS")
        for elem in listOfProcessIds:
            processID = elem['pid']
            processName = elem['name']
            processMemory = elem['memory_percent']
            processCreationTime = datetime.fromtimestamp(elem['create_time'])
            diffTime = local_time-processCreationTime
            proccessRunTimeHrs = diffTime.days * 24 + diffTime.seconds / 3600
            if proccessRunTimeHrs > processRunningTimeThreshold and processMemory >=processMemoryThreshold : 
                #os.kill(processID, signal.SIGTERM)
                logger.info("%d \t %s \t %s \t %s \t %d \t\t %f \t\t %d" % (processID,processName,processCreationTime,local_time,proccessRunTimeHrs,processMemory,elem['connections']))
        logger.info("------------------------------------------------")
    else :
        logger.info('No Running Process found')

if __name__ == '__main__':
    main()
