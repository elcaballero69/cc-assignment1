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
        GroupName="Cloud Computing TP2",
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

    # Use this for development
    # instances_m4_a = createInstance(ec2, "m4.nano", 1, SECURITY_GROUP, availability_zone_1a)
    
    # Use m4.large for deployment/demo
    instances_m4_a = createInstance(ec2, "m4.large", 1, SECURITY_GROUP, availability_zone_1a)

    instance_ids = []

    for instance in instances_m4_a:
        instance_ids.append(instance.id)

    # Wait for all instances to be active!
    instance_running_waiter = ec2_client.get_waiter('instance_running')
    instance_running_waiter.wait(InstanceIds=(instance_ids))

    return instance_ids


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
    print("Zone 1a: ", availabilityZones.get('us-east-1a'), "\n")
    # Create the instances
    ins_ids = createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones)
    print("Instance ids: \n", str(ins_ids), "\n")
    # Create the target groups

main()