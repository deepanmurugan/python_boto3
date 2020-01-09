# Simple script to fetch and constrcut the ansbile playbook dynamic inventory
# based on instance 'Name' tag

import boto3

search_tags = ['webserver*','applicationserver*']
ec2  = boto3.client("ec2")

def fetch_instance(filter_val):
    ec2_instances = ec2.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        filter_val,
                        ]
                 },
            ]
        )
    
    print(filter_val.replace("*",'')+":")
    for reservation in ec2_instances['Reservations']:
        for instance in reservation['Instances']:
            print(instance['PrivateIpAddress'])


for search_tag in search_tags:
    fetch_instance(search_tag)
