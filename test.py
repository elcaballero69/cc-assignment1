# Keys are defined in configuration file, do we need to do anything else??
import boto3
import json
import time
import subprocess
import requests
from multiprocessing import Pool
from datetime import date
from datetime import datetime, timedelta

"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'UnHealthyHostCount', 
'Dimensions': [{'Name': 'TargetGroup', 'Value': 'targetgroup/cluster1/c1e62f08981da494'}, 
                {'Name': 'LoadBalancer', 'Value': 'app/Lab1LoadBalancer/f9c86917f947d8d6'}, 
                {'Name': 'AvailabilityZone', 'Value': 'us-east-1a'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'UnHealthyHostCount', 'Timestamps': [datetime.datetime(2022, 10, 16, 23, 30, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 31, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 32, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 33, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 34, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 35, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 36, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 37, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 38, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 39, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 40, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 41, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 42, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 43, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 44, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 45, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 46, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 47, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 48, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 49, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 50, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 51, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 52, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 53, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 54, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 55, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 56, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 57, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 58, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 59, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 0, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 1, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 2, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 3, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 4, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 5, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 6, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 7, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 8, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 9, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 10, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 11, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 12, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 13, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 14, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 15, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 16, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 17, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 18, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 19, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 20, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 21, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 22, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 23, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 24, tzinfo=tzutc())], 'Values': [4.0, 6.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 12.0, 10.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': 'ab210c9e-e05b-4252-8851-8a0a3dd1c50c', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'ab210c9e-e05b-4252-8851-8a0a3dd1c50c', 'content-type': 'text/xml', 'content-length': '4907', 'date': 'Mon, 17 Oct 2022 00:25:39 GMT'}, 'RetryAttempts': 0}}
----------------------------------------
"""
"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'NewConnectionCount', 
'Dimensions': [{'Name': 'LoadBalancer', 'Value': 'app/Lab1LoadBalancer/f9c86917f947d8d6'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'NewConnectionCount', 'Timestamps': [datetime.datetime(2022, 10, 16, 23, 30, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 31, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 33, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 36, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 40, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 49, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 59, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 12, tzinfo=tzutc())], 'Values': [12.0, 8.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': '2920232e-fcf8-4fc5-89c3-1468ace65cb5', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '2920232e-fcf8-4fc5-89c3-1468ace65cb5', 'content-type': 'text/xml', 'content-length': '1184', 'date': 'Mon, 17 Oct 2022 00:25:38 GMT'}, 'RetryAttempts': 0}}
----------------------------------------
"""
"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'HTTPCode_ELB_502_Count', 
'Dimensions': [{'Name': 'LoadBalancer', 'Value': 'app/Lab1LoadBalancer/f9c86917f947d8d6'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'HTTPCode_ELB_502_Count', 'Timestamps': [datetime.datetime(2022, 10, 16, 23, 30, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 31, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 36, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 40, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 12, tzinfo=tzutc())], 'Values': [12.0, 8.0, 1.0, 1.0, 1.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': '90ee320a-42cf-4326-8941-e3d8c8554504', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '90ee320a-42cf-4326-8941-e3d8c8554504', 'content-type': 'text/xml', 'content-length': '951', 'date': 'Mon, 17 Oct 2022 00:25:37 GMT'}, 'RetryAttempts': 0}}
----------------------------------------
"""
"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'ActiveConnectionCount', 
'Dimensions': [{'Name': 'LoadBalancer', 'Value': 'app/Lab1LoadBalancer/9c021bdcb890edb4'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'ActiveConnectionCount', 'Timestamps': [datetime.datetime(2022, 10, 16, 21, 47, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 21, 58, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 22, 21, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 22, 40, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 22, 49, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 22, 53, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 4, tzinfo=tzutc())], 'Values': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': 'a6ed24ee-9191-46bb-9ec5-479f0d0398c9', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'a6ed24ee-9191-46bb-9ec5-479f0d0398c9', 'content-type': 'text/xml', 'content-length': '1107', 'date': 'Mon, 17 Oct 2022 00:25:37 GMT'}, 'RetryAttempts': 0}}
---------------------------------------
"""
"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'RequestCount', 
'Dimensions': [{'Name': 'TargetGroup', 'Value': 'targetgroup/cluster2/d64a8d3c29290081'}, 
                {'Name': 'LoadBalancer', 'Value': 'app/Lab1LoadBalancer/9c021bdcb890edb4'}, 
                {'Name': 'AvailabilityZone', 'Value': 'us-east-1c'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'RequestCount', 'Timestamps': [datetime.datetime(2022, 10, 16, 23, 23, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 24, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 25, tzinfo=tzutc())], 'Values': [0.0, 0.0, 0.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': '4a221b20-3169-40ab-a44e-5dc4d216092d', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '4a221b20-3169-40ab-a44e-5dc4d216092d', 'content-type': 'text/xml', 'content-length': '782', 'date': 'Mon, 17 Oct 2022 00:25:36 GMT'}, 'RetryAttempts': 0}}
----------------------------------------
"""
"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'RequestCountPerTarget', 
'Dimensions': [{'Name': 'TargetGroup', 'Value': 'targetgroup/cluster1/c1e62f08981da494'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'RequestCountPerTarget', 'Timestamps': [datetime.datetime(2022, 10, 16, 23, 29, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 30, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 31, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 32, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 33, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 34, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 35, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 36, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 37, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 38, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 39, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 40, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 41, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 42, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 43, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 44, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 45, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 46, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 47, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 48, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 49, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 50, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 51, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 52, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 53, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 54, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 55, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 56, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 57, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 58, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 59, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 0, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 1, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 2, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 3, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 4, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 5, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 6, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 7, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 8, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 9, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 10, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 11, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 12, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 13, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 14, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 15, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 16, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 17, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 18, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 19, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 20, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 21, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 22, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 23, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 24, tzinfo=tzutc())], 'Values': [0.0, 1.5, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': '01002a0e-b890-4643-b381-5d1af8833772', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '01002a0e-b890-4643-b381-5d1af8833772', 'content-type': 'text/xml', 'content-length': '4978', 'date': 'Mon, 17 Oct 2022 00:25:35 GMT', 'connection': 'close'}, 'RetryAttempts': 0}}
----------------------------------------
"""
"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'RequestCount', 
'Dimensions': [{'Name': 'TargetGroup', 'Value': 'targetgroup/cluster1/c1e62f08981da494'}, 
                {'Name': 'LoadBalancer', 'Value': 'app/Lab1LoadBalancer/f9c86917f947d8d6'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'RequestCount', 'Timestamps': [datetime.datetime(2022, 10, 16, 23, 29, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 30, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 31, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 32, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 33, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 34, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 35, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 36, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 37, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 38, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 39, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 40, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 41, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 42, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 43, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 44, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 45, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 46, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 47, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 48, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 49, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 50, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 51, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 52, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 53, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 54, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 55, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 56, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 57, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 58, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 59, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 0, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 1, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 2, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 3, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 4, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 5, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 6, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 7, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 8, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 9, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 10, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 11, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 12, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 13, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 14, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 15, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 16, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 17, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 18, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 19, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 20, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 21, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 22, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 23, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 24, tzinfo=tzutc())], 'Values': [0.0, 6.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': '56951e59-e30c-4da0-b3eb-e4591cb77495', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '56951e59-e30c-4da0-b3eb-e4591cb77495', 'content-type': 'text/xml', 'content-length': '4969', 'date': 'Mon, 17 Oct 2022 00:25:35 GMT'}, 'RetryAttempts': 0}}
----------------------------------------
"""
"""
{'Namespace': 'AWS/ApplicationELB', 
'MetricName': 'UnHealthyHostCount', 
'Dimensions': [{'Name': 'TargetGroup', 'Value': 'targetgroup/cluster2/adbe5ac03e1f7509'}, 
                {'Name': 'LoadBalancer', 'Value': 'app/Lab1LoadBalancer/f9c86917f947d8d6'}]}
cloudwatch data:  {'MetricDataResults': [{'Id': 'cloudwatchdata', 'Label': 'UnHealthyHostCount', 'Timestamps': [datetime.datetime(2022, 10, 16, 23, 30, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 31, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 32, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 33, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 34, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 35, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 36, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 37, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 38, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 39, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 40, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 41, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 42, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 43, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 44, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 45, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 46, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 47, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 48, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 49, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 50, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 51, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 52, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 53, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 54, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 55, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 56, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 57, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 58, tzinfo=tzutc()), datetime.datetime(2022, 10, 16, 23, 59, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 0, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 1, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 2, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 3, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 4, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 5, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 6, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 7, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 8, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 9, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 10, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 11, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 12, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 13, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 14, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 15, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 16, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 17, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 18, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 19, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 20, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 21, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 22, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 23, tzinfo=tzutc()), datetime.datetime(2022, 10, 17, 0, 24, tzinfo=tzutc())], 'Values': [10.0, 15.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 25.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0], 'StatusCode': 'Complete'}], 'Messages': [], 'ResponseMetadata': {'RequestId': '0a5048c9-8b93-49ef-af32-9f5a48344481', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '0a5048c9-8b93-49ef-af32-9f5a48344481', 'content-type': 'text/xml', 'content-length': '4951', 'date': 'Mon, 17 Oct 2022 00:25:35 GMT'}, 'RetryAttempts': 0}}
----------------------------------------
"""



def getCloudWatchMetrics(cw, startTime, ARN_targetgroup, name, ARN_LB):
    # check which metrics we want to retrieve
    # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
    #print("Start Time:", startTime)
    endTime = datetime.utcnow()
    #print("End Time:", endTime)
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
                    'Period': 10,
                    'Stat': 'Average',
                }
            },
        ],
        StartTime=startTime,
        EndTime=endTime,
        ScanBy='TimestampAscending',
    )

    print("cloudwatch data: ", data)
    print("----------------------------------------")
    return data

cw = boto3.client("cloudwatch")
startTime = datetime.today()
ARN_T2 = "arn:aws:elasticloadbalancing:us-east-1:547173889923:targetgroup/cluster2/adbe5ac03e1f7509"
ARN_M4 = "arn:aws:elasticloadbalancing:us-east-1:547173889923:targetgroup/cluster1/c1e62f08981da494"
ARN_LB = "arn:aws:elasticloadbalancing:us-east-1:547173889923:loadbalancer/app/Lab1LoadBalancer/f9c86917f947d8d6"

response = cw.list_metrics()
for each_metric in response['Metrics']:
    if(each_metric.get('Namespace')=="AWS/ApplicationELB"):
        print(each_metric)
        #data = getCloudWatchMetrics(cw, startTime, each_metric.get('Namespace'), each_metric.get('MetricName'), each_metric.get('Dimensions'))

data_T2 = getCloudWatchMetrics(cw, startTime, ARN_T2, "cluster2", ARN_LB)
data_M4 = getCloudWatchMetrics(cw, startTime, ARN_M4, "cluster1", ARN_LB)


"""
should work
MetricDataQueries=[
            {
                'Id': 'cloudwatchdata',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'UnHealthyHostCount',
                        'Dimensions': [
                            {'Name': 'TargetGroup', 'Value': ARN_targetgroup.split(':')[-1]},
                            {'Name': 'LoadBalancer', 'Value': ARN_LB.split(':')[-1].split("loadbalancer/")[-1]}]
                    },
                    'Period': 10,
                    'Stat': 'Average',
                }
            },
        ],
"""

"""
working

MetricDataQueries=[
            {
                'Id': 'cloudwatchdata',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'RequestCount',
                        'Dimensions': [
                            {
                                'Name': 'LoadBalancer',
                                'Value': ARN_LB.split(':')[-1].split("loadbalancer/")[-1]
                            }
                        ]
                    },
                    'Period': 3000,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                }
            },
        ],
"""