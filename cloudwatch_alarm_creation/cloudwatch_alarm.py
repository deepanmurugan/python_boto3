# This script is used to create a cloudwatch alaram for 
# NAT Gateway metric in all AWS Regions mentioned

# Inputs: 
# Regions - provide all regions where you want alarm to be created
# SNS Topic to be created and subscribed previosuly for all regions mentioned
# aws_account_id - your 12 digit AWS account ID

import boto3
regions = ['us-east-1','us-east-2']
aws_account_id = '87XXXXXXXXXX'
metric_name = 'ErrorPortAllocation'
name_space = 'AWS/NATGateway'
dimension_name = 'NatGatewayId'

# Create alarm using defined metrics
def create_alarm(natgatewayid, name, region):
    sns_arn = 'arn:aws:sns:'+region+':'+aws_account_id+':operations'
    cloudwatch.put_metric_alarm(
        AlarmName='NAT_Port_Allocation_Alarm_'+name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName=metric_name,
        Namespace=name_space,
        Period=60,
        Statistic='Average',
        Threshold=0,
        ActionsEnabled=True,
        AlarmActions=[sns_arn],
        AlarmDescription='Alarm when NAT Gateway port mapping crosses threshold',
        Dimensions=[
            {
            'Name': dimension_name, 
            'Value': natgatewayid
            },
        ]
    )

# Create AWS service clients and fetch Natgateway ID
for region in regions:
    print('Created client and working on Region', region)
    cloudwatch = boto3.client('cloudwatch', region_name = region)
    client = boto3.client('ec2', region_name = region)
    natgateways = client.describe_nat_gateways()
    for natgateway in natgateways['NatGateways']:
        print("Creating cloudwatch alarm for NAT ID "+natgateway['NatGatewayId']+" in region: ",region)
        for nat_tags in natgateway['Tags']:
            if 'Name' in nat_tags['Key']:
                name = nat_tags['Value']
        create_alarm(natgateway['NatGatewayId'], name, region)
