# Used to create cloudwatch dashboard based on instance tags in any region

import json, boto3, sys, math

cw  = boto3.client("cloudwatch")
ec2 = boto3.client("ec2")
my_session = boto3.session.Session()
aws_region = my_session.region_name
y = 0
y_predict = 0
widget_content = []
width, height = [6, 6]

def create_cw(dashboard_name):
    global widgets
    cf_final_template = {'widgets' : widget_content}
    cw.put_dashboard(DashboardName = dashboard_name,
                         DashboardBody = json.dumps(cf_final_template))
    widget_content.clear()

def append_cpu_utilization_template(i, loop, name, instance_type, x, y_predict):
    parameter_no = 0
    y = y_predict + parameter_no * height 
    metric_title = name+"-CPUUsed"
    cf_template = {
    "type": "metric",
    "width": 6,
    "height": 6,
    "x": x,
    "y": y,
    "properties": {
        "metrics": [
            [ "AWS/EC2", "CPUUtilization", "InstanceId", i ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-2",
        "title": metric_title 
        }
    }
    widget_content.append(cf_template)

def append_networkin_template(i, loop, name, instance_type, x, y_predict):
    print("creating cw template for instance: " +i)
    parameter_no = 1
    y = y_predict + parameter_no * height 
    metric_title = name+'-NetworkIn'
    cf_template_networkin = {
    "type": "metric",
    "width": 6,
    "height": 6,
    "x": x,
    "y": y,
    "properties": {
        "metrics": [
            [ "AWS/EC2", "NetworkIn", "InstanceId", i ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-2",
        "title": metric_title
        }
    }
    widget_content.append(cf_template_networkin)

def append_networkout_template(i, loop, name, instance_type, x, y_predict):
    parameter_no = 2 
    y = y_predict + parameter_no * height
    metric_title = name+'-NetworkOut'
    cf_template_networkout = {
    "type": "metric",
    "width": 6,
    "height": 6,
    "x": x,
    "y": y,
    "properties": {
        "metrics": [
            [ "AWS/EC2", "NetworkOut", "InstanceId", i ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-2",
        "title": metric_title
        }
    }
    widget_content.append(cf_template_networkout)

def append_diskwritebytes_template(i, loop, name, instance_type, x, y_predict):
    parameter_no = 3 
    y = y_predict + parameter_no * height 
    metric_title = name+'-DiskWriteBytes'
    cf_template_diskwritebytes = {
    "type": "metric",
    "width": 6,
    "height": 6,
    "x": x,
    "y": y,
    "properties": {
        "metrics": [
            [ "AWS/EC2", "DiskWriteBytes", "InstanceId", i ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-2",
        "title": metric_title 
        }
    }
    widget_content.append(append_diskwritebytes_template)

def append_diskwrites_template(i, loop, name, instance_type, x, y_predict):
    parameter_no = 4 
    y = y_predict + parameter_no * height 
    metric_title = name+'-DiskWriteBytes'
    cf_template_diskwritebytes = {
    "type": "metric",
    "width": 6,
    "height": 6,
    "x": x,
    "y": y,
    "properties": {
        "metrics": [
            [ "AWS/EC2", "DiskWriteBytes", "InstanceId", i ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-2",
        "title": metric_title
        }
    }
    widget_content.append(cf_template_diskwritebytes)


def instance_count(instances):
    count = 0
    for r in instances['Reservations']:
        for i in r['Instances']:
            count += 1
    return count

def instance_search():
    no_of_parameter = 5
    dashboard_params = {'Test_Dashboard': ['*-server', 'vpc*'], 'Test_Dashboard_again': ['vpc*']}
    strip_string = ['-server', '-server']
    loop_count = 0
    for dashboard_name, filter_val in dashboard_params.items():
        y_predict = 0
        print(dashboard_name)
        instances = ec2.describe_instances(
        Filters = [{'Name':'tag:Name', 'Values':filter_val}
                ])
        inst_count = instance_count(instances)
        print(inst_count)
        loop = 0
        for r in instances['Reservations']:
            for i in r['Instances']:
                for t in i['Tags']:
                    if 'Name' in t['Key']:
                        name = t['Value'].strip(strip_string[loop_count])
                x_predict = loop % 4 
                x = x_predict * width
                if loop > 3:
                    y_predict = no_of_parameter * math.floor(loop/4) * height
                append_cpu_utilization_template(i["InstanceId"], loop, name, i["InstanceType"], x, y_predict)
                append_networkin_template(i["InstanceId"], loop, name, i["InstanceType"], x, y_predict)
                append_networkout_template(i["InstanceId"], loop, name, i["InstanceType"], x, y_predict)
                append_diskwritebytes_template(i["InstanceId"], loop, name, i["InstanceType"], x, y_predict)
                append_diskwrites_template(i["InstanceId"], loop, name, i["InstanceType"], x, y_predict)
                loop += 1
        create_cw(dashboard_name)
        loop_count += 1

instance_search()
