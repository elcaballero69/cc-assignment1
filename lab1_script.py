# Keys are defined in configuration file, do we need to do anything else??
import boto3
import json
import time
import subprocess
import requests
from multiprocessing import Pool
from datetime import date
from datetime import datetime

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
    return 'Hello, World from ' + ec2_metadata.instance_id + ' which is a ' ec2_metadata.instance_type + ' instance'
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
        },{
            'FromPort': 80,
            'ToPort': 80,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },{
            'FromPort': 8080,
            'ToPort': 8080,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )

    SECURITY_GROUP = [group_id]
    print("security_group: ", SECURITY_GROUP)

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
    # CODE TO CREATE INSTANCES STARTS HERE
    # Creating 9 instances

    # Get wanted availability zone
    availability_zone_1a = availabilityZones.get('us-east-1a')
    availability_zone_1b = availabilityZones.get('us-east-1b')
    availability_zone_1c = availabilityZones.get('us-east-1c')

    print("availability zone 1a: ", availability_zone_1a)
    print("availability zone 1b: ", availability_zone_1b)
    print("availability zone 1c: ", availability_zone_1c)

    # Types: t2.large and m4.large use these for demo

    # instances_t2_a = createInstance(ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1a)
    # instances_m4_a = createInstance(ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1a)
    # instances_t2_b = createInstance(ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1b)
    # instances_m4_b = createInstance(ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1b)
    # instances_t2_c = createInstance(ec2, "t2.large", 1, SECURITY_GROUP, availability_zone_1c)

    # Use this for development
    instances_t2_a = createInstance(ec2, "t2.micro", 2, SECURITY_GROUP, availability_zone_1a)
    instances_m4_a = createInstance(ec2, "t2.nano", 2, SECURITY_GROUP, availability_zone_1a)
    instances_t2_b = createInstance(ec2, "t2.micro", 2, SECURITY_GROUP, availability_zone_1b)
    instances_m4_b = createInstance(ec2, "t2.nano", 2, SECURITY_GROUP, availability_zone_1b)
    instances_t2_c = createInstance(ec2, "t2.micro", 1, SECURITY_GROUP, availability_zone_1c)

    print("t2 instanses zone a: ", instances_t2_a)

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

    print("T2_instance_ids", T2_instance_ids)
    print("M4_instance_ids", M4_instance_ids)
    print("instance_ids", instance_ids)

    return instance_ids, T2_instance_ids, M4_instance_ids


def createInstance2(ec2_client, ec2, INSTANCE_TYPE, COUNT, SECURITY_GROUP, SUBNET_ID):
    # Don't change these
    KEY_NAME = "vockey"
    INSTANCE_IMAGE = "ami-08d4ac5b634553e16"

    return ec2_client.run_instances(
        ImageId=INSTANCE_IMAGE,
        MinCount=COUNT,
        MaxCount=COUNT,
        Monitoring={'Enabled':True},
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=SECURITY_GROUP,
        SubnetId=SUBNET_ID,
        UserData=userdata
    )


def createInstances2(ec2_client, ec2, SECURITY_GROUP, availabilityZones):
    # CODE TO CREATE INSTANCES STARTS HERE
    # Creating 9 instances

    # Get wanted availability zone
    availability_zone_1a = availabilityZones.get('us-east-1a')
    availability_zone_1b = availabilityZones.get('us-east-1b')
    availability_zone_1c = availabilityZones.get('us-east-1c')

    print("availability zone 1a: ", availability_zone_1a)
    print("availability zone 1b: ", availability_zone_1b)
    print("availability zone 1c: ", availability_zone_1c)

    # Types: t2.large and m4.large

    instances_t2_a = createInstance(ec2_client, ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1a)
    instances_m4_a = createInstance(ec2_client, ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1a)
    instances_t2_b = createInstance(ec2_client, ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1b)
    instances_m4_b = createInstance(ec2_client, ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1b)
    instances_t2_c = createInstance(ec2_client, ec2, "t2.large", 1, SECURITY_GROUP, availability_zone_1c)

    print("T2 instances for availability zone a: ", instances_t2_a)

    instance_ids = []
    T2_instance_ids = []
    M4_instance_ids = []

    for instance in instances_t2_a['Instances']:
        instance_ids.append(instance['InstanceId'])
        T2_instance_ids.append({'Id': instance['InstanceId']})

    for instance in instances_m4_a['Instances']:
        instance_ids.append(instance['InstanceId'])
        M4_instance_ids.append({'Id': instance['InstanceId']})

    for instance in instances_t2_b['Instances']:
        instance_ids.append(instance['InstanceId'])
        T2_instance_ids.append({'Id': instance['InstanceId']})

    for instance in instances_m4_b['Instances']:
        instance_ids.append(instance['InstanceId'])
        M4_instance_ids.append({'Id': instance['InstanceId']})

    for instance in instances_t2_c['Instances']:
        instance_ids.append(instance['InstanceId'])
        T2_instance_ids.append({'Id': instance['InstanceId']})

    # Wait for all instances to be active!
    instance_running_waiter = ec2_client.get_waiter('instance_running')
    instance_running_waiter.wait(InstanceIds=(instance_ids))

    print("T2_instance_ids", T2_instance_ids)
    print("M4_instance_ids", M4_instance_ids)
    print("instance_ids", instance_ids)

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

    print("Target group T2: ", targetGroupT2)
    print("Target group M4: ", targetGroupM4)

    # get targetGroupARN
    ARN_T2 = targetGroupT2['TargetGroups'][0].get('TargetGroupArn')
    ARN_M4 = targetGroupM4['TargetGroups'][0].get('TargetGroupArn')

    return ARN_T2, ARN_M4


def assignInstancesToTargetGroups(elbv2, ARN_T2, ARN_M4, T2_instance_ids, M4_instance_ids):
    # assign instances to target groups
    # wait for instances to be created properly
    # time.sleep(25)
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

    print("target group Instances_T2: \n", targetgroupInstances_T2)
    print("target group Instances_M4: \n", targetgroupInstances_M4)
    # For now only print
    print("Health: \n", health)
    return targetgroupInstances_T2, targetgroupInstances_M4


def createLoadBalancer(elbv2, SECURITY_GROUP, availabilityZones):
    # will most probably need more arguments
    # need to decide what typ of load balancer it should be
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

    print("Load Balancer: \n", loadBalancer)
    DNS_LB = loadBalancer['LoadBalancers'][0].get('DNSName')
    ARN_LB = loadBalancer['LoadBalancers'][0].get('LoadBalancerArn')
    print("Load Balancer dns: ", DNS_LB)
    print("Load Balancer ARN: ", ARN_LB)
    return DNS_LB, ARN_LB




def assignTargetGroupsToLoadBalancer(elbv2, ARN_LB, ARN_T2, ARN_M4):
    # assign target groups to load balancer

    listener = elbv2.create_listener(
            LoadBalancerArn=ARN_LB,
            Port=80,
            Protocol='HTTP',
            #create default listener
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

    print("listener: ", listener)
    ARN_Listener = listener['Listeners'][0].get('ListenerArn')
    print("listener_ARN:", ARN_Listener)

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
    print("rule:", rule)

    return rule

def getCloudWatchMetrics(cw, startTime, ARN_targetgroup):
    # check which metrics we want to retrieve
    # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
    data = cw.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'cloudwatchdata',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'HealthyHostCount',
                        'Dimensions': [
                            {
                                'Name': 'TargetGroup',
                                'Value': 'string'
                            },
                        ]
                    },
                    'Period': 1,
                    'Stat': 'Minimum',
                }
            },
        ],
        StartTime=startTime,
        EndTime=datetime.now(),
        ScanBy='TimestampAscending',
    )

    print("cloudwatch data: ", data)
    return data


def values(ec2_client, instance_ids):
    instance_data_raw = ec2_client.describe_instances(InstanceIds=instance_ids)
    instance_list = instance_data_raw["Reservations"][0]["Instances"]

    # Example Get IP address
    ins_ips = []
    for res_id in range(len(instance_data_raw["Reservations"])):
        for ins_id in range(len(instance_data_raw["Reservations"][res_id]["Instances"])):
            ins_ips.append(instance_data_raw["Reservations"][res_id]["Instances"][ins_id]["PublicIpAddress"])
    print("Instance IP adresses: ", ins_ips)
    return ins_ips

# Functions to deploy flask

def loop_subprocess(ins_ips):
    counter = 0
    for ins_ip in ins_ips:
        counter += 1
        subprocess.call(['sh', './lab1_flask.sh', ins_ip, str(counter)])
        print(500 * "-")
        print(str(ins_ip) + " has flask deployed!")

def call_endpoint_http(DNS_LB, cluster):
    url = "http://"+ DNS_LB + "?cluster=" + cluster
    headers = {'content-type': 'application/json'}
    r = requests.get(url, headers=headers)
    print(r.content)





def main():
    ec2_client = boto3.client("ec2")
    ec2 = boto3.resource('ec2')
    elbv2 = boto3.client('elbv2')
    cw = boto3.client('cloudwatch')

    startTime = datetime.now()
    SECURITY_GROUP, vpc_id = createSecurityGroup(ec2_client)
    availabilityZones = getAvailabilityZones(ec2_client)
    ins_ids, T2_instance_ids, M4_instance_ids = createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones)
    ARN_T2, ARN_M4 = createTargetGroups(elbv2, vpc_id)
    targetgroupInstances_T2, targetgroupInstances_M4 = assignInstancesToTargetGroups(elbv2, ARN_T2, ARN_M4, T2_instance_ids, M4_instance_ids)
    DNS_LB, ARN_LB = createLoadBalancer(elbv2, SECURITY_GROUP, availabilityZones)
    ARN_Listener = assignTargetGroupsToLoadBalancer(elbv2, ARN_LB, ARN_T2, ARN_M4)
    make_rule(elbv2, ARN_Listener, ARN_T2, 1, 'cl2')
    make_rule(elbv2, ARN_Listener, ARN_M4, 2, 'cl1')

    #wait until load balancer is available
    print('WAITING FOR AVAILABILITY OF LOAD BALANCER...')
    lb_waiter = elbv2.get_waiter('load_balancer_available')
    lb_waiter.wait(LoadBalancerArns=[ARN_LB])
    ins_ips = values(ec2_client, ins_ids)

    #request the flask server
    print('REQUESTS ARE RUNNNING')
    for i in range(0,100):
        print(f'REQUEST {i}')
        call_endpoint_http(DNS_LB, 'cl1')
        call_endpoint_http(DNS_LB, 'cl2')
        time.sleep(5)
    print('REQUESTS TERMINATED')

    data_T2 = getCloudWatchMetrics(cw, startTime, ARN_T2)
    data_M4 = getCloudWatchMetrics(cw, startTime, ARN_M4)

main()