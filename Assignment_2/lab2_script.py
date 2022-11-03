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

import botocore
import paramiko
import os
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# import webbrowser

# This makes the plots made by the script open in a webbrowser
# mpl.use('WebAgg')


userdata_hadoop="""#!/bin/bash
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
wget -d --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36" https://www.gutenberg.org/cache/epub/4300/pg4300.txt.utf8.gzip
cp pg4300.txt.utf8.gzip pg4300.txt.gz
gunzip -kv pg4300.txt.gz
mkdir input
mv pg4300.txt input
"""

userdata_spark="""#!/bin/bash
sudo apt-get update
yes | sudo apt install default-jdk scala git -y
sudo apt-get install wget
sudo wget https://archive.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
sudo tar xvf spark-*
sudo mv spark-3.0.1-bin-hadoop2.7 /opt/spark
sudo cat << EOF >> .profile
export SPARK_HOME=/opt/spark
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
EOF
source ~/.profile
sudo apt install python3-pip
y | pip install urllib3
pip install pandas
pip install flask
pip install xlsxwriter
pyspark
import urllib3
import pandas as pd
import time
http = urllib3.PoolManager()
LINKS = ['http://www.gutenberg.ca/ebooks/buchanj-midwinter/buchanj-midwinter-00-t.txt',
         'http://www.gutenberg.ca/ebooks/carman-farhorizons/carman-farhorizons-00-t.txt',
         'http://www.gutenberg.ca/ebooks/colby-champlain/colby-champlain-00-t.txt',
         'http://www.gutenberg.ca/ebooks/cheyneyp-darkbahama/cheyneyp-darkbahama-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-bumps/delamare-bumps-00-t.txt',
         'http://www.gutenberg.ca/ebooks/charlesworth-scene/charlesworth-scene-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-lucy/delamare-lucy-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-myfanwy/delamare-myfanwy-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-penny/delamare-penny-00-t.txt'
         ]
result = pd.DataFrame()
start = time.time()
for i in range(0,3):
    for link in LINKS:
        r = http.request('GET', link)
        content = r.data.decode('latin-1')
        content = content.replace('\n',' ')
        rdd = sc.parallelize(content.split(' '))
        rdd = rdd.map(lambda x: (x,1))
        rdd = rdd.reduceByKey(lambda x,y: x + y).sortByKey()
        df = rdd.toDF(['Word', f'Count_Link{str(LINKS.index(link))}']).toPandas().sort_values(f'Count_Link{str(LINKS.index(link))}', axis=0, ascending = False).set_index('Word')
        if i == 0:
            result = pd.concat([result, df], axis=1)
            df.to_excel('~/wordcount_file.xlsx', engine = 'xlsxwriter')
end = time.time()
with open("elapsed_time.txt", "w") as f:
    f.write(str(end-start))
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


def createInstance(ec2, INSTANCE_TYPE, COUNT, SECURITY_GROUP, SUBNET_ID, userdata):
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

def createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones, userdata):
    # Get wanted availability zone
    availability_zone_1a = availabilityZones.get('us-east-1a')

    """Use this for development to save funds"""
    # instances_m4_a = createInstance(ec2, "m4.nano", 1, SECURITY_GROUP, availability_zone_1a)

    # Use m4.large for deployment/demo
    instances_m4_a = createInstance(ec2, "m4.large", 1, SECURITY_GROUP, availability_zone_1a, userdata)

    instance_ids = []

    instance_ids.append(instances_m4_a[0].id)

    instances_m4_a[0].wait_until_running()
    instances_m4_a[0].reload()

    ip = instances_m4_a[0].public_ip_address
    print(ip)

    # Wait for all instances to be active!
    instance_running_waiter = ec2_client.get_waiter('instance_running')
    instance_running_waiter.wait(InstanceIds=(instance_ids))

    return [instance_ids, ip]

def send_command(client, command):
    try:
        stdin, stdout, stderr = client.exec_command(command)
        print("stderr.read():", stderr.read())
        #output = stdout.read().decode('ascii').split("\n")
        print("stdout", stdout.read())
    except:
        print("error occured in sending command")

def get_execution_time(client, command):
    try:
        stdin, stdout, stderr = client.exec_command(command)
        print("stderr.read():", stderr.read())
        output = stdout.read().decode('ascii').split("\n")
        print("stdout", output)
        time_real = output[1].split("\t")
        return time_real[1]
    except:
        print("error occured in getting execution time")


def compare_Hadoop_vs_Linux_worcount(ip):
    accesKey = paramiko.RSAKey.from_private_key_file("C:/Users/meste/PycharmProjects/CloudComputing/cc-assignment1/Assignment_2/labsuser.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")

    # performing the map reduce tasks
    print("Execution time for linux and hadoop")
    res_linux = send_command(client, "{ time cat input/pg4300.txt | tr ' ' '\n' | sort | uniq -c  ; } 2> time_linux.txt")
    res_hadoop = send_command(client, 'source ~/.profile \n { time hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/input/pg4300.txt output 2> hadoop.stderr  ; } 2> time_hadoop.txt')

    # retrieving the execution time
    print("retrieving the execution time for linux and hadoop")
    linux_time = get_execution_time(client, 'cat time_linux.txt')
    hadoop_time = get_execution_time(client, 'cat time_hadoop.txt')

    print("\nExecution time for Hadoop is:", hadoop_time)
    print("Execution time for Linux is:", linux_time, '\n')

    client.close()

def waiter(ec2_client, ins_hadoop, ins_spark):

    ready = False
    accesKey = paramiko.RSAKey.from_private_key_file("C:/Users/meste/PycharmProjects/CloudComputing/cc-assignment1/Assignment_2/labsuser.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while (ready == False):
        try:
            client.connect(hostname=ins_hadoop[1], username="ubuntu", pkey=accesKey)
            #client.connect(hostname=ins_spark[1], username="ubuntu", pkey=accesKey)
            print("testing connection")
        except:
            time.sleep(10)
        else:
            client.close()
            print("instances up and running")
            ready = True

    return True

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
    ins_hadoop = createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones, userdata_hadoop)
    print("Instance ids: \n", str(ins_hadoop[0]), "\n")
    print("Instance ip: \n", str(ins_hadoop[1]), "\n")
    ins_spark = createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones, userdata_spark)
    print("Instance ids: \n", str(ins_spark[0]), "\n")
    print("Instance ip: \n", str(ins_spark[1]), "\n")

    """-------------------Run Wordcount experiment--------------------------"""
    print("Wait installation")
    time.sleep(300)
    """start_time = time.time()
    running = waiter(ec2_client, ins_hadoop, ins_spark)
    end_time = time.time()
    print("Waiting time:", end_time-start_time)"""
    print("Comparing Hadoop vs linux in wordcount")
    compare_Hadoop_vs_Linux_worcount(ins_hadoop[1])
    print("Check the instance: \n", str(ins_hadoop[1]), "\n")
    """-------------------Get output--------------------------"""

    """-------------------plot and compare--------------------------"""

    """-------------------Write MapReduce program--------------------------"""

    """-------------------Run Recomendation System--------------------------"""

main()
