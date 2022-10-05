# AWS LAB
## CURRENTLY WORKING ON:
Aura:\
Cedric: D\
Nick:\
Victor\

## BEFORE USING: 
- Download AWS CLI: https://aws.amazon.com/cli/
- Make sure .aws/credentials file has security keys and access token
    - These can be downloaded from https://awsacademy.instructure.com/courses/24020/modules/items/1970541
    - Select AWS Details from menu and under "Cloud access", "AWS CLI:" click "Show"
    - Copy content to the .aws/configuration file
- Make sure .aws/config file has following content:
    [default]
    region=us-east-1
    output=json
- Install boto3 with pip

## DONE:
- Creation of 9 instances
- Creation of security group
- creation of target groups
- assigning all instances to the target groups

## LAB GOALS:
Create  clusters using EC2 and ELB
Benchmark clusters to compare performance
Automate solution
Report findings
Make demo

