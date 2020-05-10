#!/usr/bin/env python

import boto3
import psutil
import requests
import os
import subprocess

_METADATAURL = 'http://169.254.169.254/latest/meta-data'

cmd = "curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region"
run = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
output = run.communicate()[0]
os.environ['AWS_DEFAULT_REGION'] = output.strip()

cw = boto3.client('cloudwatch')
currMetrics = []
def appendMetrics(CurrentMetrics, Dimensions, Name, Unit, Value):
    metric = { 'MetricName' : Name
    , 'Dimensions' : Dimensions
    , 'Unit' : Unit
    , 'Value' : Value
    }
    CurrentMetrics.append(metric)


def usedMemoryPercentage():
    return psutil.virtual_memory().percent

def usedDiskSpace():
    return psutil.disk_usage('/').percent

if __name__ == '__main__':
    instance_id = requests.get( _METADATAURL + '/instance-id').text
    instance_type = requests.get( _METADATAURL + '/instance-type').text
    dimensions = [{'Name' : 'InstanceID', 'Value' : instance_id}, {'Name' : 'InstanceType', 'Value' : instance_type}]
    appendMetrics(currMetrics, dimensions, Name='MemoryInUse', Value=usedMemoryPercentage(), Unit='Percent')
    appendMetrics(currMetrics, dimensions, Name='DiskSpaceUsed', Value=usedDiskSpace(), Unit='Percent')
    response = cw.put_metric_data(MetricData = currMetrics, Namespace='CustomMetrics')
