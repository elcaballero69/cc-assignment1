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
import matplotlib.pyplot as plt
import matplotlib as mpl
# import webbrowser

# allows us to geth the path for the pem file
from pathlib import Path

def get_project_root() -> Path:
    """
    Function for getting the path where the program is executed
    @ return: returns the parent path of the path were the program is executed
    """
    return Path(__file__).parent

# This makes the plots made by the script open in a webbrowser
# mpl.use('WebAgg')

"""
The user data constants are used to setup and download programs on the instances
They are passed as arguments in the create instance step
"""

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
sudo apt install default-jdk scala git -y
sudo apt-get install wget
sudo wget https://archive.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
sudo tar xvf spark-*
sudo mv spark-3.0.1-bin-hadoop2.7 /opt/spark
sudo cat << EOF >> .profile
export SPARK_HOME=/opt/spark
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
EOF
yes | sudo apt install python3-pip
pip install urllib3
pip install pyspark
"""

def createSecurityGroup(ec2_client):
    """
        The function creates a new security group in AWS
        The function retrievs the vsp_id from the AWS portal, as it is personal and needed for creating a new group
        It then creates the security group using boto3 package
        then it waits for the creation
        then it assigns new rules to the security group

        Parameters
        ----------
        ec2_client
            client that allows for sertain functions using boto3

        Returns
        -------
        SECURITY_GROUP : list[str]
            list of the created security group ids
        vpc_id : str
            the vpc_id as it is needed for other operations

        Errors
        -------
        The function throws an error if a security group with the same name already exists in your AWS

    """
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
        }]
    )

    SECURITY_GROUP = [group_id]
    return SECURITY_GROUP, vpc_id

def getAvailabilityZones(ec2_client):
    """
        Retrieving the subnet ids for availability zones
        they are required to assign for example instances to a specific availabilityzone

        Parameters
        ----------
        ec2_client
            client of boto3 tho access certain methods related to AWS EC2

        Returns
        -------
        dict
            a dictonary, with availability zone name as key and subnet id as value

        """
    # Availability zones
    response = ec2_client.describe_subnets()

    availabilityzones = {}
    for subnet in response.get('Subnets'):
        # print(subnet)
        availabilityzones.update({subnet.get('AvailabilityZone'): subnet.get('SubnetId')})

    return availabilityzones

def createInstance(ec2, INSTANCE_TYPE, COUNT, SECURITY_GROUP, SUBNET_ID, userdata):
    """
        function that creates EC2 instances on AWS

        Parameters
        ----------
        ec2 : client
            ec2 client to perform actions on AWS EC2 using boto3
        INSTANCE_TYPE : str
            name of the desired instance type.size
        COUNT : int
            number of instances to be created
        SECURITY_GROUP : array[str]
            array of the security groups that should be assigned to the instance
        SUBNET_ID : str
            subnet id that assigns the instance to a certain availability zone
        userdata : str
            string that setups and downloads programs on the instance at creation

        Returns
        -------
        array
            list of all created instances, including their data

        """
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
    """
        function that retrievs and processes attributes as well as defining the amount and types of instances to be created
        getting the decired subnet id
        calling function create instance to create the instances
        parces the return to just return the ids and ips of the instances
        currently handle only creation of one instance

        Parameters
        ----------
        ec2_client : client
            Boto3 client to access certain function to controll AWS CLI
        ec2 : client
            Boto3 client to access certain function to controll AWS CLI
        SECURITY_GROUP : array[str]
            list of security groups to assign to instances
        availabilityZones : dict{str, str}
            dict of availability zone names an key and subnet ids as value
        userdata : str
            script to setup instances

        Returns
        -------
        array
            containg instance id and ip
        """
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

def getParamikoClient():
    """
        Retrievs the users PEM file and creates a paramiko client required to ssh into the instances

        Returns
        -------
        client
            the paramiko client
        str
            the access key from the PEM file

        """
    path = str(get_project_root()).replace('\\', '/')
    print("path", path)
    accesKey = paramiko.RSAKey.from_private_key_file(path + "/labsuser.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    return client, accesKey

def send_command(client, command):
    """
        function that sends command to an instance using paramiko
        print possible errors and return values

        Parameters
        ----------
        client : client
            the paramiko client required to connect to the intance usin ssh
        command : str
            The desired commands are sent to the instance

        Returns
        -------
        str
            returns the return value of commands

        """
    try:
        stdin, stdout, stderr = client.exec_command(command)
        # the read() function reads the output in bit form
        print("stderr.read():", stderr.read())
        print("stdout", stdout.read())
        # converts the bit string to str
        output = stdout.read().decode('ascii').split("\n")

        return output
    except:
        print("error occured in sending command")

def get_execution_time(client, command):
    """
        we save the execution time in the instance as a text file
        we retrieve this file to be able to display and plot the execution times

        Parameters
        ----------
        client : client
            paramiko client to ssh into instance
        command : str
            command string that we want to execute

        Returns
        -------
        str
            the time in stringformat 0m7.898s

        """
    try:
        stdin, stdout, stderr = client.exec_command(command)
        print("stderr.read():", stderr.read())
        output = stdout.read().decode('ascii').split("\n")
        print("stdout", output)
        time_real = output[1].split("\t")

        return time_real[1]
    except:
        print("error occured in getting execution time")

def compare_Hadoop_vs_Linux_worcount(ip, client, accesKey):
    """
        performing the benchmarking between linux and hadoop.
        connecting to instance using paramiko client
        Performing the wordcount using both systems
        retrieve the excution times of both executions
        prints the times for comparison
        closes client

        Parameters
        ----------
        ip : str
            ip adress of the instance we wish to connect to
        client : client
            paramiko client to ssh into instance
        accesKey : str
            private accesskey to gain access to instance
    """

    try:
        client.connect(hostname=ip, username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")

    # performing the map reduce tasks
    print("Execution time for linux and hadoop")
    res_linux = send_command(client, "{ time cat input/pg4300.txt | tr ' ' '\n' | sort | uniq -c  ; } 2> time_linux.txt")
    res_hadoop = send_command(client, 'source ~/.profile \n '
                                      '{ time hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/input/pg4300.txt output 2> hadoop.stderr  ; } 2> time_hadoop.txt')

    # retrieving the execution time
    print("retrieving the execution time for linux and hadoop")
    linux_time = get_execution_time(client, 'cat time_linux.txt')
    hadoop_time = get_execution_time(client, 'cat time_hadoop.txt')

    print("\nExecution time for Hadoop is:", hadoop_time)
    print("Execution time for Linux is:", linux_time, '\n')

    client.close()

def addNewInputfiles(client, accesKey, ip_hadoop):
    """
        creates a new directory and adds new input files to it on the instance
        these are required to perform the benchmarking between hadoop and spark

        connects to instance
        adds files
        closes client

        Parameters
        ----------
        client : client
            paramiko client to ssh into instance
        accesKey : str
            peronsonal key to gain access to instance
        ip_hadoop : str
            ip of the hadoop instance,  to gain access to specific client

        """
    try:
        client.connect(hostname=ip_hadoop, username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")

    # setting up new input files for hadoop, for the second benchmarking scenario
    print("Setting up new input files for hadoop")
    res = send_command(client, "mkdir wordcountinput \n "
                               "cd wordcountinput \n"
                               "sudo wget https://tinyurl.com/4vxdw3pa \n"
                               "sudo wget https://tinyurl.com/kh9excea \n"
                               "sudo wget https://tinyurl.com/dybs9bnk \n"
                               "sudo wget https://tinyurl.com/datumz6m \n"
                               "sudo wget https://tinyurl.com/j4j4xdw6 \n"
                               "sudo wget https://tinyurl.com/ym8s5fm4 \n"
                               "sudo wget https://tinyurl.com/2h6a75nk \n"
                               "sudo wget https://tinyurl.com/vwvram8 \n"
                               "sudo wget https://tinyurl.com/weh83uyn \n"
                               "cd ../")

    client.close()

def runWordcountHadoop(client, accesKey, ip_hadoop):
    """
        running the second wordcount example on hadoop for three iterations for the benchmarking

        connect to instance
        run wordcount
        close client

        Parameters
        ----------
        client : client
            paramiko client to ssh into instance
        accesKey : str
            peronsonal key to gain access to instance
        ip_hadoop : str
            ip of the hadoop instance,  to gain access to specific client

        """
    try:
        client.connect(hostname=ip_hadoop, username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")

    # setting up new input files for hadoop, for the second benchmarking scenario
    print("Running wordcount on hadoop for three iterations")
    for x in range(1, 4):
        res = send_command(client, 'source ~/.profile \n '
                            '{ time hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/wordcountinput output' + str(x) + ' 2> hadoop' + str(x) + '.stderr  ; } 2> time_hadoop' + str(x) + '.txt')

    client.close()

def getHadoopWordcountRunTime(client, accesKey, ip_hadoop):
    """
        retrieves the execution time from the execution time files from the instance for the second wordcount

        Parameters
        ----------
        client : client
            paramiko client to ssh into instance
        accesKey : str
            peronsonal key to gain access to instance
        ip_hadoop : str
            ip of the hadoop instance,  to gain access to specific client

        Returns
        -------
        array[str]
            array of the execution times for hadoop benchmarking

        """
    try:
        client.connect(hostname=ip_hadoop, username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")

    # setting up new input files for hadoop, for the second benchmarking scenario
    print("Running wordcount on hadoop for three iterations")
    hadoop_wordcount_time = []
    for x in range(1, 4):
        hadoop_wordcount_time.append(get_execution_time(client, 'cat time_hadoop' + str(x) + '.txt'))

    client.close()
    print(hadoop_wordcount_time)
    return hadoop_wordcount_time

def changeStrToTime(hadoop_wordcount_time_str):
    """
        transforming the string formatted time into time format
        required to plot correctly

        Parameters
        ----------
        hadoop_wordcount_time_str : array[str]
            array of the execution times in str format

        Returns
        -------
        array[time]
            array of the execution times in time format

        """
    hadoop_wordcount_time = []
    for x in hadoop_wordcount_time_str:
        time = x.replace('m', ':').replace('s', '').replace('.', ':')
        hadoop_wordcount_time.append(datetime.strptime(time, '%M:%S:%f'))
    return hadoop_wordcount_time

def plot_time(hadoop_wordcount_time, title):
    """
        plotting the execution times for visual benchmarking

        Parameters
        ----------
        hadoop_wordcount_time : array[time]
            array of the execution times in time format
        title : str
            title for the plot

        """
    plt.plot(hadoop_wordcount_time, 'bo--')
    plt.title(title)
    plt.ylabel("Execution Time")
    plt.xlabel("Iteration")
    plt.show()


def runWordcountSpark(client, accesKey, ip_spark):
    """
                running the second wordcount example on spark using python code for the benchmarking

                connect to instance
                enter pyspark environment
                run python code on instance
                close client

                Parameters
                ----------
                client : client
                    paramiko client to ssh into instance
                accesKey : str
                    peronsonal key to gain access to instance
                ip_spark : str
                    ip of the spark instance, to gain access to specific client

                """
    try:
        client.connect(hostname=ip_spark, username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")

    # setting up new input files for hadoop, for the second benchmarking scenario
    res = send_command(client, 'sudo wget https://raw.githubusercontent.com/elcaballero69/cc-assignment1/main/Assignment_2/spark_wordcount.py')
    res = send_command(client, "source ~/.profile \n "
                               "pyspark \n "
                               "exec(open('spark_wordcount.py').read())")


    client.close()

def main():
    """
        main function fer performing the application

        Conncets to the boto3 clients
        calls the required functions

        """
    """------------Get necesarry clients from boto3------------------------"""
    ec2_client = boto3.client("ec2")
    ec2 = boto3.resource('ec2')

    """------------Create Paramiko Client------------------------------"""
    paramiko_client, accesKey = getParamikoClient()

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

    """-------------------Run Wordcount experiment hadoop vs linux--------------------------"""
    print("Wait installation")
    time.sleep(420)
    print("Comparing Hadoop vs linux in wordcount")
    compare_Hadoop_vs_Linux_worcount(ins_hadoop[1], paramiko_client, accesKey)
    print("Check the instance: \n", str(ins_hadoop[1]), "\n")

    """-------------------Run Wordcount experiment hadoop vs spark--------------------------"""
    addNewInputfiles(paramiko_client, accesKey, ins_hadoop[1])
    runWordcountHadoop(paramiko_client, accesKey, ins_hadoop[1])
    runWordcountSpark(paramiko_client, accesKey, ins_spark[1])
    """-------------------Get output--------------------------"""
    hadoop_wordcount_time_str = getHadoopWordcountRunTime(paramiko_client, accesKey, ins_hadoop[1])
    """-------------------plot and compare--------------------------"""
    hadoop_wordcount_time = changeStrToTime(hadoop_wordcount_time_str)
    plot_time(hadoop_wordcount_time, "Hadoop Wordcount Execution Time")
    print("done")
    """-------------------Write MapReduce program--------------------------"""

    """-------------------Run Recomendation System--------------------------"""

main()
