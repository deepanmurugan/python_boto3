# This lambda function is used to create ec2 snapshot daily for 
# all the EBS volume which is currently in-use status
# Ignore if Autobackup tag is set to No for any ebs volume
# By default Autobackup tag is set to Yes
# Script will delete the snapshots whichever are older than retention period

import boto3
from botocore.exceptions import ClientError
from datetime import datetime,timedelta

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions().get('Regions',[] )
    for region in regions:
        print ("Checking region ", region['RegionName'])
        reg=region['RegionName']
        ec2 = boto3.client('ec2', region_name=reg)
        take_snapshot(reg, ec2)
        delete_snapshot(reg, ec2)

def take_snapshot(reg, ec2):
    result = ec2.describe_volumes( Filters=[{'Name': 'status', 'Values': ['in-use']}])
    ec2resource = boto3.resource('ec2', region_name=reg)
    backup = 'Yes'
    for volume in result['Volumes']:
        print(volume)
        for tag in volume['Tags']:
            if tag['Key'] == 'Autobackup':
                backup = tag.get('Value') 
        if backup == 'No':
            break

        print("Backing up ", volume['VolumeId'], volume['AvailabilityZone'])
        result = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description='Created by Lambda function')
        snapshot = ec2resource.Snapshot(result['SnapshotId'])

        volumename = 'N/A'
        if 'Tags' in volume:
            for tags in volume['Tags']:
                if tags["Key"] == 'Name':
                    volumename = tags["Value"]

        snapshot.create_tags(Tags=[{'Key': 'Name','Value': volumename}])


def delete_snapshot(reg, ec2):
    now = datetime.now()
    account_id = '690646717512'
    retention_days = 3
    result = ec2.describe_snapshots( OwnerIds=[account_id] )
    
    for snapshot in result['Snapshots']:
            print("Checking snapshot for retention period", snapshot['SnapshotId'])
            snapshot_time = snapshot['StartTime'].replace(tzinfo=None)
            if (now - snapshot_time) > timedelta(retention_days):
                print("Snapshot is older thabn retention days and deleting it")
                try:
                    ec2resource = boto3.resource('ec2', region_name=reg)
                    snapshot = ec2resource.Snapshot(snapshot['SnapshotId'])
                    snapshot.delete()
                except ClientError as e:
                    print("Caught exception", e)
            else:
                print("Snapshot is newer than configured retention of %d days so we keep it")
