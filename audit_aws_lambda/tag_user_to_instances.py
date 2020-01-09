# Script is used to create the tag 'Launched_by' and provide the value whoever launched it
# We are using cloudtrail to monitor the activities and upload the activity to S3 bucket
# Using athena to create tables out of S3 bucket and fetching the RunInstances activity -
# and creating EC2 instance tag.
#
# Run the Lambda once per day to check all the created instances for the previous day -
# and tag them appropriately based on cloudtrail event logs.
#
# Rename the variables accordingly


import json
import boto3
import time
from datetime import datetime

s3 = boto3.client('s3')
athena = boto3.client('athena')
s3_resource = boto3.resource('s3')

table_name = 'your_table_for_cloudtrail_logs'
regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
s3_input = 's3://s3-bucket-you-configured-for-cloudtrail-logs/AWSLogs/XXXXXXXXXXXX/CloudTrail/'
database = 'sampledb'
s3_output = 's3://your-s3-lambda-output-bucket/'
awsevent = 'RunInstances'
ec2_details = []
partition_day = datetime.now().day - 1
partition_month = datetime.now().month
partition_year = datetime.now().year
if partition_day < 10:
    partition_day = str(partition_day).zfill(2)
if partition_month < 10:
    partition_month = str(partition_month).zfill(2)


# Creating tags based on the instance details fetched
def tag_instances(executionID):
    loop = 0
    obj = s3_resource.Object('your-s3-lambda-output-bucket', executionID+".csv")
    contents=obj.get()['Body'].read().decode(encoding="utf-8",errors="ignore")
    for line in contents.splitlines():
        if loop > 0:
            user = line.split(',')[0].replace('"','')
            ec2_instance = line.split(',')[1].replace('"','')
            ec2_region = line.split(',')[2].replace('"','')
            ec2 = boto3.client('ec2', region_name = ec2_region)
            try:
                response = ec2.describe_instance_status(InstanceIds=[ec2_instance])
                print("Instance exists and creating tags", ec2_instance)
                ec2.create_tags(
                    DryRun=False,
                    Resources=[
                        ec2_instance,
                    ],
                    Tags=[
                        {
                            'Key': 'Launched By',
                            'Value': user
                        },
                    ]
                )
            except Exception as e:
                print(e)
                print("Tag not creating for this instance, see above exception for details", ec2_instance)
        loop = loop + 1


#Executing the athena query to fetch instance and user details
def get_results(executionID):
    retries = 0
    status = athena.get_query_execution(
    QueryExecutionId=executionID
    )
    print(status['QueryExecution']['Status']['State'])
    results = athena.get_query_results(
    QueryExecutionId=executionID
    )
    tag_instances(executionID)


# Fetch the launched instance details from athena table
def get_instance_launch():
    for region in regions:
        instance_query = str("SELECT useridentity.username username,json_extract(responseelements, '$.instancesSet.items[0].instanceId') instanceid, region FROM "+ table_name +" WHERE region='"
        + region + "' and year='"
        + str(partition_year) + "' and month='" 
        + str(partition_month) + "' and date='"
        + str(partition_day) + "' and eventname='"
        + awsevent + "';")
        query_response = athena.start_query_execution(
        QueryString=instance_query,
        QueryExecutionContext={
            'Database': database
            },
        ResultConfiguration={
            'OutputLocation': s3_output,
            }
        )
        time.sleep(12)
        get_results(query_response['QueryExecutionId'])
    

# Query to load the S3 partitions in athena
def lambda_handler(event, context):
    for region in regions:
        query = str("ALTER TABLE "+ table_name +" ADD PARTITION (region='"
        + region + "',year="
        + str(partition_year) + ",month=" 
        + str(partition_month) + ",date="
        + str(partition_day)
        + ") location '"+s3_input
        + region
        + "/" + str(partition_year)
        + "/" + (partition_month) + "/"
        + str(partition_day) + "';")
        query_response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
            },
        ResultConfiguration={
            'OutputLocation': s3_output,
            }
        )
    get_instance_launch()
