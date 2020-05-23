#!/usr/bin/python
import subprocess
import socket
import ast
import datetime
import ConfigParser
import boto
from boto.route53.record import ResourceRecordSets

all_node_health_stat = []
health_stat = {}

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(('/home/ubuntu/failover.conf'))

def read_config(prop, label='DEFAULT'):
    global CONFIG
    return CONFIG.get(label, prop)

def handle_os_cmd(parms_list):
    p = subprocess.Popen(parms_list, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout,stderr = p.communicate()
    return stdout, stderr, p.returncode

def check_master():
    dns_fqdn = read_config('dns_fqdn')
    resp, err, ret_code = handle_os_cmd('dig +short {}'.format(dns_fqdn))
    if (not ret_code) and resp:
        master_node = resp.split()[0]
        print "Master Node {} is up, no issues...".format(master_node)

    resp, err, ret_code = handle_os_cmd('nc -vz {} {} > /dev/null; if ! [ $? -eq 0 ]; then exit 2; fi;'.format(dns_fqdn, healthcheck_port))
    if ret_code != 0:
        print "Master Node is down... checking for next node to promote as master..."
        get_all_node_health()

def get_all_node_health():
    for node in all_node_health_stat:
        resp, err, ret_code = handle_os_cmd('nc -vz {} {} > /dev/null; if ! [ $? -eq 0 ]; then exit 2; fi;'.format(node, healthcheck_port))
        if ret_code == 0:
            health_stat.update({str(node): 'up'})
        else:
            health_stat.update({str(node): 'down'})
    promote_to_master()

def promote_to_master():
    this_node = socket.gethostbyname(socket.gethostname())
    for node in all_node_health_stat:
        if health_stat[node] != 'down' and this_node != node:
            print "Waiting for another priority node {} to become leader....".format(node)
            break
        elif health_stat[node] == 'up' and this_node == node:
            msg = "[{:%Y-%b-%d %H:%M:%S}] Node {} is highest priority node to be promoted and updating master DNS...".format(datetime.datetime.now(), this_node)
            print msg
            update_dns(this_node)

def update_dns(this_node):
    zoneid = read_config('zone_id')
    aws_key = read_config('aws_key')
    secret_key = read_config('secret_key')

    conn = boto.connect_route53(aws_access_key_id=aws_key, aws_secret_access_key=secret_key)
    changes = ResourceRecordSets(conn, zoneid, '')
    change = changes.add_change("UPSERT", dns_fqdn, "A", ttl=10)
    change.add_value(this_node)
    result = changes.commit()
    msg = "[{:%Y-%b-%d %H:%M:%S}] Updating FQDN={} to IP={}. response={}".format(datetime.datetime.now(), dns_fqdn, local_ip, result)
    print msg


if __name__ == "__main__":
    all_node_health_stat = ast.literal_eval(read_config('all_nodes')) 
    dns_fqdn = read_config('dns_fqdn')
    zone_id = read_config('zone_id')
    aws_key = read_config('aws_key')
    secret_key = read_config('secret_key')
    healthcheck_port = read_config('healthcheck_port')
    check_master()
