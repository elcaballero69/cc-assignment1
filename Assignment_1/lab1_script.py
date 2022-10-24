# Keys are defined in configuration file
# MAKE SURE YOU UPDATED YOUR .AWS/credentials file
# MAKE SURE boto3, matplotlib, requests and tornado are all installed using pip
import boto3
import json
import time
import subprocess
import requests
from multiprocessing import Pool
from datetime import date
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import webbrowser

# This makes the plots made by the script open in a webbrowser
mpl.use('WebAgg')
userdata="""#!/bin/bash
cd /home/ubuntu
mkdir flask_app
sudo apt-get update
yes | sudo apt-get install python3-venv
cd flask_app
python3 -m venv venv
source venv/bin/activate
pip install flask
pip install ec2_metadata
cat <<EOF >flask_app.py
from flask import Flask
from ec2_metadata import ec2_metadata
app = Flask(__name__)
@app.route('/')
def flask_app():
    return 'Hello, World from ' + ec2_metadata.instance_id
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
EOF
flask --app flask_app run --host 0.0.0.0 --port 80
"""

def createSecurityGroup(ec2_client):
    # Create security group, using SSH & HHTP access available from anywhere
    groups = ec2_client.describe_security_groups()
    vpc_id = groups["SecurityGroups"][0]["VpcId"]

    new_group = ec2_client.create_security_group(
        Description="SSH and HTTP access",
        GroupName="Cloud Computing TP1",
        VpcId=vpc_id
    )

    # Wait for the security group to exist!
    new_group_waiter = ec2_client.get_waiter('security_group_exists')
    new_group_waiter.wait(GroupNames=["Cloud Computing TP1"])

    group_id = new_group["GroupId"]

    rule_creation = ec2_client.authorize_security_group_ingress(
        GroupName="Cloud Computing TP1",
        GroupId=group_id,
        IpPermissions=[{
            'FromPort': 22,
            'ToPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'FromPort': 80,
            'ToPort': 80,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'FromPort': 8080,
            'ToPort': 8080,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )

    SECURITY_GROUP = [group_id]
    return SECURITY_GROUP, vpc_id

def getAvailabilityZones(ec2_client):
    # Availability zones
    response = ec2_client.describe_subnets()

    availabilityzones = {}
    for subnet in response.get('Subnets'):
        # print(subnet)
        availabilityzones.update({subnet.get('AvailabilityZone'): subnet.get('SubnetId')})

    return availabilityzones

def createInstance(ec2, INSTANCE_TYPE, COUNT, SECURITY_GROUP, SUBNET_ID):
    # Don't change these
    KEY_NAME = "vockey"
    INSTANCE_IMAGE = "ami-08d4ac5b634553e16"

    return ec2.create_instances(
        ImageId=INSTANCE_IMAGE,
        MinCount=COUNT,
        MaxCount=COUNT,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=SECURITY_GROUP,
        SubnetId=SUBNET_ID,
        UserData=userdata
    )

def createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones):
    # Get wanted availability zone
    availability_zone_1a = availabilityZones.get('us-east-1a')
    availability_zone_1b = availabilityZones.get('us-east-1b')
    availability_zone_1c = availabilityZones.get('us-east-1c')

    # Use this for development
    # instances_t2_a = createInstance(ec2, "t2.micro", 2, SECURITY_GROUP, availability_zone_1a)
    # instances_m4_a = createInstance(ec2, "t2.nano", 2, SECURITY_GROUP, availability_zone_1a)
    # instances_t2_b = createInstance(ec2, "t2.micro", 2, SECURITY_GROUP, availability_zone_1b)
    # instances_m4_b = createInstance(ec2, "t2.nano", 2, SECURITY_GROUP, availability_zone_1b)
    # instances_t2_c = createInstance(ec2, "t2.micro", 1, SECURITY_GROUP, availability_zone_1c)
    
    # Use t2.large and m4.large for deployment/demo
    instances_t2_a = createInstance(ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1a)
    instances_m4_a = createInstance(ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1a)
    instances_t2_b = createInstance(ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1b)
    instances_m4_b = createInstance(ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1b)
    instances_t2_c = createInstance(ec2, "t2.large", 1, SECURITY_GROUP, availability_zone_1c)

    instance_ids = []
    T2_instance_ids = []
    M4_instance_ids = []

    for instance in instances_t2_a:
        instance_ids.append(instance.id)
        T2_instance_ids.append({'Id': instance.id})

    for instance in instances_m4_a:
        instance_ids.append(instance.id)
        M4_instance_ids.append({'Id': instance.id})

    for instance in instances_t2_b:
        instance_ids.append(instance.id)
        T2_instance_ids.append({'Id': instance.id})

    for instance in instances_m4_b:
        instance_ids.append(instance.id)
        M4_instance_ids.append({'Id': instance.id})

    for instance in instances_t2_c:
        instance_ids.append(instance.id)
        T2_instance_ids.append({'Id': instance.id})

    # Wait for all instances to be active!
    instance_running_waiter = ec2_client.get_waiter('instance_running')
    instance_running_waiter.wait(InstanceIds=(instance_ids))

    return instance_ids, T2_instance_ids, M4_instance_ids

def createTargetgroup(elbv2, vpc_id, name):

    return elbv2.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id
    )

def createTargetGroups(elbv2, vpc_id):
    # create target groups
    targetGroupT2 = createTargetgroup(elbv2, vpc_id, "cluster2")
    targetGroupM4 = createTargetgroup(elbv2, vpc_id, "cluster1")

    # get targetGroupARN
    ARN_T2 = targetGroupT2['TargetGroups'][0].get('TargetGroupArn')
    ARN_M4 = targetGroupM4['TargetGroups'][0].get('TargetGroupArn')

    return ARN_T2, ARN_M4

def assignInstancesToTargetGroups(elbv2, ARN_T2, ARN_M4, T2_instance_ids, M4_instance_ids):
    targetgroupInstances_T2 = elbv2.register_targets(
        TargetGroupArn=ARN_T2,
        Targets=T2_instance_ids
    )
    targetgroupInstances_M4 = elbv2.register_targets(
        TargetGroupArn=ARN_M4,
        Targets=M4_instance_ids
    )
    health = elbv2.describe_target_groups(
        TargetGroupArns=[ARN_T2, ARN_M4]
    )
    return targetgroupInstances_T2, targetgroupInstances_M4

def createLoadBalancer(elbv2, SECURITY_GROUP, availabilityZones):
    loadBalancer=elbv2.create_load_balancer(
        Name="Lab1LoadBalancer",
        Subnets=[
            availabilityZones.get('us-east-1a'),
            availabilityZones.get('us-east-1b'),
            availabilityZones.get('us-east-1c')
        ],
        SecurityGroups=SECURITY_GROUP,
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )

    # print("Load Balancer: \n", loadBalancer)
    DNS_LB = loadBalancer['LoadBalancers'][0].get('DNSName')
    ARN_LB = loadBalancer['LoadBalancers'][0].get('LoadBalancerArn')
    return DNS_LB, ARN_LB

def assignTargetGroupsToLoadBalancer(elbv2, ARN_LB, ARN_T2, ARN_M4):
    # Assign target groups to load balancer
    listener = elbv2.create_listener(
            LoadBalancerArn=ARN_LB,
            Port=80,
            Protocol='HTTP',
            # Create default listener
            DefaultActions=[
                {
                    'ForwardConfig': {
                        'TargetGroups': [
                            {
                                'TargetGroupArn': ARN_T2,
                                'Weight': 1
                            },
                            {
                                'TargetGroupArn': ARN_M4,
                                'Weight': 1
                            }
                        ]
                    },
                    'Type': 'forward'
                }
            ]
        )

    # print("listener: ", listener)
    ARN_Listener = listener['Listeners'][0].get('ListenerArn')
    return ARN_Listener

def make_rule(elbv2, ARN_Listener, ARN, priority, path):
    rule = elbv2.create_rule(
        ListenerArn=ARN_Listener,
        Conditions=[{
            'Field': 'query-string',
            'QueryStringConfig': {
                'Values': [
                    {
                        'Key': 'cluster',
                        'Value': path
                   }
                ]
            },
        }],
        Priority=priority,
        Actions=[
            {'Type': 'forward',
            'TargetGroupArn': ARN}
        ]
    )
    return rule

def getCloudWatchMetrics(cw, startTime, ARN_targetgroup, name, ARN_LB):
    # check which metrics we want to retrieve
    # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
    print("Start Time:", startTime)
    endTime = datetime.utcnow()
    print("End Time:", endTime)
    data = cw.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'cloudwatchdata',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'UnHealthyHostCount',
                        'Dimensions': [
                            {
                                'Name': 'TargetGroup',
                                'Value': ARN_targetgroup.split(':')[-1]
                            },
                            {
                                'Name': 'LoadBalancer',
                                'Value': ARN_LB.split(':')[-1].split("loadbalancer/")[-1]
                            }
                        ]
                    },
                    'Period': 60,
                    'Stat': 'Maximum',
                }
            },
        ],
        StartTime=startTime,
        EndTime=endTime,
        ScanBy='TimestampAscending',
    )

    print("cloudwatch data: ", data)
    return data

def createPolicy(iam):
    my_policy = {
      "Version": "2012-10-17",
      "Statement": [{
          "Effect": "Allow",
          "Action":
              ["cloudwatch:GetMetricData"],
          "Resource": "*"
        }]
    }

    policy = iam.create_policy(
        PolicyName='CloudwatchPolicy',
        PolicyDocument=json.dumps(my_policy)
    )

    # print("policy:", policy)
    return policy

def call_endpoint_http(DNS_LB, cluster):
    url = "http://"+ DNS_LB + "?cluster=" + cluster
    headers = {'content-type': 'application/json'}
    r = requests.get(url, headers=headers)
    print(r.content)

def plotData(data_t2, data_m4):
    values_t2 = data_t2['MetricDataResults'][0].get('Values')
    time_t2 = data_t2['MetricDataResults'][0].get('Timestamps')
    print("Values:", values_t2)

    values_m4 = data_m4['MetricDataResults'][0].get('Values')
    time_m4 = data_m4['MetricDataResults'][0].get('Timestamps')
    print("Values:", values_t2)

    plt.subplot(1, 2, 1)
    plt.plot(time_m4, values_m4)
    plt.ylabel('Unhealhy Hosts')
    plt.xlabel('Timestamp')
    plt.xticks(rotation=45)
    plt.yticks([0, 1, 2, 3, 4, 5, 6])
    plt.title("Cluster 1, M4.Large")

    plt.subplot(1, 2, 2)
    plt.plot(time_t2, values_t2)
    plt.ylabel('Unhealhy Hosts')
    plt.xlabel('Timestamp')
    plt.xticks(rotation=45)
    plt.yticks([0, 1, 2, 3, 4, 5, 6])
    plt.title("Cluster 2, T2.Large")

    plt.show()



def main():
    # Get necesarry clients from boto3
    ec2_client = boto3.client("ec2")
    ec2 = boto3.resource('ec2')
    elbv2 = boto3.client('elbv2')
    cw = boto3.client('cloudwatch')
    iam = boto3.client('iam')
    startTime = datetime.utcnow()
    # Create security group
    SECURITY_GROUP, vpc_id = createSecurityGroup(ec2_client)
    print("security_group: ", SECURITY_GROUP)
    print("vpc_id: ", str(vpc_id), "\n")
    # Create policy
    policy = createPolicy(iam)
    print("Cloud watch policy created \n")
    # Get availability Zones
    availabilityZones = getAvailabilityZones(ec2_client)
    print("Availability zones:")
    print("Zone 1a: ", availabilityZones.get('us-east-1a'))
    print("Zone 1b: ", availabilityZones.get('us-east-1b'))
    print("Zone 1c: ", availabilityZones.get('us-east-1c'), "\n")
    # Create the instances
    ins_ids, T2_instance_ids, M4_instance_ids = createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones)
    print("Instance ids: \n", str(ins_ids), "\n")
    print("Instance ids T2: \n", str(T2_instance_ids), "\n")
    print("Instance ids M42: \n", str(M4_instance_ids), "\n")
    # Create the target groups
    ARN_T2, ARN_M4 = createTargetGroups(elbv2, vpc_id)
    print("Target group T2 ARN: ", ARN_T2)
    print("Target group M4 ARN: ", ARN_M4, "\n")
    # Assign instances to the target groups
    targetgroupInstances_T2, targetgroupInstances_M4 = assignInstancesToTargetGroups(elbv2, ARN_T2, ARN_M4, T2_instance_ids, M4_instance_ids)
    # Create the load balancer
    DNS_LB, ARN_LB = createLoadBalancer(elbv2, SECURITY_GROUP, availabilityZones)
    print("Load Balancer DNS: ", DNS_LB)
    print("Load Balancer ARN: ", ARN_LB, "\n")
    # Create Listener
    ARN_Listener = assignTargetGroupsToLoadBalancer(elbv2, ARN_LB, ARN_T2, ARN_M4)
    print("listener_ARN:", ARN_Listener, "\n")
    # Add rules for cluster based routing
    make_rule(elbv2, ARN_Listener, ARN_T2, 1, 'cl2')
    make_rule(elbv2, ARN_Listener, ARN_M4, 2, 'cl1')
    #wait until load balancer is available
    print('WAITING FOR AVAILABILITY OF LOAD BALANCER...')
    lb_waiter = elbv2.get_waiter('load_balancer_available')
    lb_waiter.wait(LoadBalancerArns=[ARN_LB])
    # Open up browser tab with the Loadbalancer
    webbrowser.open(DNS_LB)
    # Open up browser tabs for cluster based routing
    webbrowser.open(DNS_LB + '?cluster=cl1')
    webbrowser.open(DNS_LB + '?cluster=cl2')
    # Request the flask server
    print('REQUESTS ARE RUNNNING')
    for i in range(0, 1200):
        print(f'REQUEST {i}')
        call_endpoint_http(DNS_LB, 'cl1')
        call_endpoint_http(DNS_LB, 'cl2')
        time.sleep(0.1)
    print('REQUESTS TERMINATED')
    data_T2 = getCloudWatchMetrics(cw, startTime, ARN_T2, "cluster2", ARN_LB)
    data_M4 = getCloudWatchMetrics(cw, startTime, ARN_M4, "cluster1", ARN_LB)
    plotData(data_T2, data_M4)
main()