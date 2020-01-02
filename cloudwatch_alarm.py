# This script is used to create a cloudwatch alaram for 
# NAT Gateway metric in all AWS Regions mentioned

# Inputs: 
# Regions - provide all regions where you want alarm to be created
# SNS Topic to be created and subscibed previosuly for all regions mentioned
# aws_account_id - your 12 digit AWS account ID

import boto3
regions = ['us-east-1','us-east-2']
aws_account_id = '8XXXXXXXXXXX'

# Create alarm using defined metrics
def create_alarm(natgatewayid, name, region):
    sns_arn = 'arn:aws:sns:'+region+':'+aws_account_id+':operations'
    cloudwatch.put_metric_alarm(
        AlarmName='NAT_Port_Allocation_Alarm_'+name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='ErrorPortAllocation',
        Namespace='AWS/NATGateway',
        Period=60,
        Statistic='Average',
        Threshold=0,
        ActionsEnabled=False,
        AlarmActions=[sns_arn],
        AlarmDescription='Alarm when NAT Gateway port mapping crosses threshold',
        Dimensions=[
            {
            'Name': 'NatGatewayId',
            'Value': natgatewayid
            },
        ],
        Unit='Seconds'
    )

# Create AWS service clients and fetch Nategaway ID
for region in regions:
    print('created client for region', region)
    cloudwatch = boto3.client('cloudwatch', region_name = region)
    client = boto3.client('ec2', region_name = region)
    natgateways = client.describe_nat_gateways()
    for natgateway in natgateways['NatGateways']:
        print("Creating cloudwatch alarm for NAT ID "+natgateway['NatGatewayId']+" in region: ",region)
        #print(natgateway['NatGatewayId'])
        for nat_tags in natgateway['Tags']:
            if 'Name' in nat_tags['Key']:
                name = nat_tags['Value']
        create_alarm(natgateway['NatGatewayId'], name, region)
