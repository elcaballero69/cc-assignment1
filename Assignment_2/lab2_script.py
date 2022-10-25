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
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import webbrowser

# This makes the plots made by the script open in a webbrowser
# mpl.use('WebAgg')
userdata="""#!/bin/bash
cd /home/ubuntu
sudo apt-get update
yes | sudo apt install openjdk-11-jdk-headless
sudo apt-get install wget
wget https://dlcdn.apache.org/hadoop/common/stable/hadoop-3.3.4.tar.gz
sudo tar -xf hadoop-3.3.4.tar.gz -C /usr/local/
cat << EOF >> .profile
#!/bin/sh
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=\$JAVA_HOME/bin:\$PATH
#!/bin/sh
export HADOOP_PREFIX=/usr/local/hadoop-3.3.4
export PATH=\$HADOOP_PREFIX/bin:\$PATH
EOF
sudo chmod ugo+rw /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh
cat << EOF >> /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh
# export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
# export HADOOP_PREFIX=/usr/local/hadoop-3.3.4
EOF
source .profile
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
    new_group_waiter.wait(GroupNames=["Cloud Computing TP2"])

    group_id = new_group["GroupId"]

    rule_creation = ec2_client.authorize_security_group_ingress(
        GroupName="Cloud Computing TP2",
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

    """Use this for development to save funds"""
    # instances_m4_a = createInstance(ec2, "m4.nano", 1, SECURITY_GROUP, availability_zone_1a)

    # Use m4.large for deployment/demo
    instances_m4_a = createInstance(ec2, "m4.large", 1, SECURITY_GROUP, availability_zone_1a)

    instance_ids = []

    instance_ids.append(instances_m4_a[0].id)

    # Wait for all instances to be active!
    instance_running_waiter = ec2_client.get_waiter('instance_running')
    instance_running_waiter.wait(InstanceIds=(instance_ids))

    return instance_ids



def main():
    """------------Get necesarry clients from boto3------------------------"""
    ec2_client = boto3.client("ec2")
    ec2 = boto3.resource('ec2')
    elbv2 = boto3.client('elbv2')
    cw = boto3.client('cloudwatch')
    iam = boto3.client('iam')

    """-------------------Create security group--------------------------"""
    SECURITY_GROUP, vpc_id = createSecurityGroup(ec2_client)
    print("security_group: ", SECURITY_GROUP)
    print("vpc_id: ", str(vpc_id), "\n")

    """-------------------Get availability Zones--------------------------"""
    availabilityZones = getAvailabilityZones(ec2_client)
    print("Availability zones:")
    print("Zone 1a: ", availabilityZones.get('us-east-1a'), "\n")

    """-------------------Create the instances--------------------------"""
    ins_ids = createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones)
    print("Instance ids: \n", str(ins_ids), "\n")

    """-------------------Run Wordcount experiment--------------------------"""

    """-------------------Get output--------------------------"""

    """-------------------plot and compare--------------------------"""

    """-------------------Write MapReduce program--------------------------"""

    """-------------------Run Recomendation System--------------------------"""



main()