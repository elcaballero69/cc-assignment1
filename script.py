# Keys are defined in configuration file, do we need to do anything else??
import boto3
import json
import time

ec2_client = boto3.client("ec2")
ec2 = boto3.resource('ec2')
elbv2 = boto3.client('elbv2')


def createInstances(ec2, INSTANCE_TYPE, COUNT, SECURITY_GROUP, SUBNET_ID):
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
    )

def main(ec2_client, ec2, elbv2):

    # CODE TO CREATE INSTANCES STARTS HERE
    # Creating 10 instances 

    # Create security group, using only SSH access available from anywhere

    groups = ec2_client.describe_security_groups()
    vpc_id = groups["SecurityGroups"][0]["VpcId"]

    new_group = ec2_client.create_security_group(
        Description="SSH all",
        GroupName="Cloud Computing TP1",
        VpcId=vpc_id
    )

    group_id = new_group["GroupId"]

    rule_creation = ec2_client.authorize_security_group_ingress(
        GroupName="Cloud Computing TP1",
        GroupId=group_id,
        IpPermissions=[{
            'FromPort': 22,
            'ToPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )

    SECURITY_GROUP = [group_id]

    print(SECURITY_GROUP)

    # Availability zones

    response = ec2_client.describe_subnets()

    availabilityzones = {}
    for subnet in response.get('Subnets'):
            #print(subnet)
            availabilityzones.update({subnet.get('AvailabilityZone'): subnet.get('SubnetId')})

    #print(availabilityzones)

    # Get wanted availability zone
    availability_zone_1a = availabilityzones.get('us-east-1a')
    availability_zone_1b = availabilityzones.get('us-east-1b')
    availability_zone_1c = availabilityzones.get('us-east-1c')

    print(availability_zone_1a)

    # Types: t2.large and m4.large, testing with micro

    instances_t2_a = createInstances(ec2, "t2.large", 2, SECURITY_GROUP,availability_zone_1a)
    instances_m4_a = createInstances(ec2, "m4.large", 2, SECURITY_GROUP,availability_zone_1a)
    instances_t2_b = createInstances(ec2, "t2.large", 2, SECURITY_GROUP,availability_zone_1b)
    instances_m4_b = createInstances(ec2, "m4.large", 2, SECURITY_GROUP,availability_zone_1b)
    instances_t2_c = createInstances(ec2, "t2.large", 1, SECURITY_GROUP,availability_zone_1c)

    print(instances_t2_a)

    instance_ids = []

    for instance in instances_t2_a:
        instance_ids.append(instance.id)

    for instance in instances_m4_a:
        instance_ids.append(instance.id)

    for instance in instances_t2_b:
        instance_ids.append(instance.id)

    for instance in instances_m4_b:
        instance_ids.append(instance.id)

    for instance in instances_t2_c:
        instance_ids.append(instance.id)

    print(instance_ids)

    # create target groups
    targetGroupT2 = elbv2.create_target_group(
        Name="targetGroupT2",
        Protocol='TCP',
        Port=80,
        VpcId=vpc_id
    )
    targetGroupM4 = elbv2.create_target_group(
        Name="targetGroupM4",
        Protocol='TCP',
        Port=80,
        VpcId=vpc_id
    )

    print(targetGroupT2)
    print(targetGroupM4)

    # get targetGroupARN
    print(targetGroupT2['TargetGroups'])
    print(targetGroupT2['TargetGroups'][0])
    print(targetGroupT2['TargetGroups'][0].get('TargetGroupArn'))
    ARN_T2=targetGroupT2['TargetGroups'][0].get('TargetGroupArn')
    ARN_M4 = targetGroupM4['TargetGroups'][0].get('TargetGroupArn')

    # assign instances to target groups
    time.sleep(15)
    targetgroupInstances_T2 = elbv2.register_targets(
        TargetGroupArn=ARN_T2,
        Targets=[
            {
                'Id': instance_ids[0]
            }
        ]
    )

    print(targetgroupInstances_T2)



def values(ec2_client, instance_ids):
    # test 
    # time.sleep(10)
    
    """
    ------
    THE INSTANCES ARE CREATED AS THEY SHOULD, HOWEVER WE ARE UNABLE TO GET THE DATA FOR THEM,
    BECAUSE THEY ARE NOT FOUND YET, SCRIPT IS TOO FAST AND AWS TOO SLOW

    HOWEVER, WE ARE NOT SURE IF WE ACTUALLY NEED THIS, DEPENDS ON HOW WE CAN CONNECT TO THE INSTANCES
    ------
    """

    #  list of ids : [id,id,id]

    instance_data_raw = ec2_client.describe_instances(InstanceIds=instance_ids)

    # returns a list with a lot of paramaeters for each instance, PublicIpAddress parameter has the Public IPv4 address used for connection

    instance_list = instance_data_raw["Reservations"][0]["Instances"]
    print(len(instance_list))

    print(len(instance_data_raw["Reservations"]))

    # Example Get IP address
    ins_ids = []

    for res_id in range(len(instance_data_raw["Reservations"])):
        for ins_id in range(len(instance_data_raw["Reservations"][res_id]["Instances"])):
            ins_ids.append(instance_data_raw["Reservations"][res_id]["Instances"][ins_id]["PublicIpAddress"])

    print(ins_ids)


main(ec2_client, ec2, elbv2)