# Keys are defined in configuration file, do we need to do anything else??
import boto3
import json
import time
import subprocess
from multiprocessing import Pool


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
        }]
    )

    SECURITY_GROUP = [group_id]
    print(SECURITY_GROUP)

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
        SubnetId=SUBNET_ID
    )


def createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones):
    # CODE TO CREATE INSTANCES STARTS HERE
    # Creating 9 instances

    # Get wanted availability zone
    availability_zone_1a = availabilityZones.get('us-east-1a')
    availability_zone_1b = availabilityZones.get('us-east-1b')
    availability_zone_1c = availabilityZones.get('us-east-1c')

    print(availability_zone_1a)
    print(availability_zone_1b)
    print(availability_zone_1c)

    # Types: t2.large and m4.large

    instances_t2_a = createInstance(ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1a)
    instances_m4_a = createInstance(ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1a)
    instances_t2_b = createInstance(ec2, "t2.large", 2, SECURITY_GROUP, availability_zone_1b)
    instances_m4_b = createInstance(ec2, "m4.large", 2, SECURITY_GROUP, availability_zone_1b)
    instances_t2_c = createInstance(ec2, "t2.large", 1, SECURITY_GROUP, availability_zone_1c)

    print(instances_t2_a)

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

    print(T2_instance_ids)
    print(M4_instance_ids)
    print(instance_ids)

    return instance_ids, T2_instance_ids, M4_instance_ids

def createTargetgroup(elbv2, vpc_id, name):

    return elbv2.create_target_group(
        Name=name,
        Protocol='TCP',
        Port=80,
        VpcId=vpc_id
    )

def createTargetGroups(elbv2, vpc_id):
    # create target groups
    targetGroupT2 = createTargetgroup(elbv2, vpc_id, "targetGroupT2")
    targetGroupM4 = createTargetgroup(elbv2, vpc_id, "targetGroupM4")

    print(targetGroupT2)
    print(targetGroupM4)

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

    print(targetgroupInstances_T2)
    print(targetgroupInstances_M4)

    return targetgroupInstances_T2, targetgroupInstances_M4

    #TODO create load balancer
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
    )

    print(loadBalancer)

    ARN_LB = loadBalancer['LoadBalancers'][0].get('LoadBalancerArn')
    print(ARN_LB)

    return ARN_LB


def assignTargetGroupsToLoadBalancer(elbv2, ARN_LB, ARN_T2, ARN_M4):
    # assign target groups to load balancer
    listener = elbv2.create_listener(
        LoadBalancerArn=ARN_LB,
        Port=80,
        Protocol='HTTP',
        DefaultActions=[
            {
                'Order': 1,
                'Type': 'forward',
                'ForwardConfig': {
                    'TargetGroups': [
                        {
                            'TargetGroupArn': ARN_T2,
                            'Weight': 123
                        },
                        {
                            'TargetGroupArn': ARN_M4,
                            'Weight': 123
                        },
                    ]
                }
            },
        ]
    )

    print(listener)

    return listener


def values(ec2_client, instance_ids):
    instance_data_raw = ec2_client.describe_instances(InstanceIds=instance_ids)
    instance_list = instance_data_raw["Reservations"][0]["Instances"]

    # Example Get IP address
    ins_ips = []
    for res_id in range(len(instance_data_raw["Reservations"])):
        for ins_id in range(len(instance_data_raw["Reservations"][res_id]["Instances"])):
            ins_ips.append(instance_data_raw["Reservations"][res_id]["Instances"][ins_id]["PublicIpAddress"])
    print(ins_ips)
    return ins_ips

# Functions to deploy flask

def loop_subprocess(ins_ips):
    for ins_ip in ins_ips:
        subprocess.call(['sh', './lab1_flask.sh', ins_ip])
        print(500 * "-")
        print(str(ins_ip) + " has flask deployed!")

def main():
    ec2_client = boto3.client("ec2")
    ec2 = boto3.resource('ec2')
    elbv2 = boto3.client('elbv2')

    SECURITY_GROUP, vpc_id = createSecurityGroup(ec2_client)
    availabilityZones = getAvailabilityZones(ec2_client)
    ins_ids, T2_instance_ids, M4_instance_ids = createInstances(ec2_client, ec2, SECURITY_GROUP, availabilityZones)
    ARN_T2, ARN_M4 = createTargetGroups(elbv2, vpc_id)
    targetgroupInstances_T2, targetgroupInstances_M4 = assignInstancesToTargetGroups(elbv2, ARN_T2, ARN_M4, T2_instance_ids, M4_instance_ids)
    ARN_LB = createLoadBalancer(elbv2, SECURITY_GROUP, availabilityZones)
    listener = assignTargetGroupsToLoadBalancer(elbv2, ARN_LB, ARN_T2, ARN_M4)
    ins_ips = values(ec2_client, ins_ids)
    loop_subprocess(ins_ips)

main()