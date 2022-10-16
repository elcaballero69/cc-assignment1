# Keys are defined in configuration file, do we need to do anything else??
import boto3
import json
import time
import subprocess
import requests
from multiprocessing import Pool
from datetime import date
from datetime import datetime, timedelta

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
                        'MetricName': 'RequestCount',
                        'Dimensions': [
                            {
                                'Name': 'LoadBalancer',
                                'Value': ARN_LB.split(':')[-1].split("loadbalancer/")[-1]
                            }
                        ]
                    },
                    'Period': 3000,
                    'Stat': 'Sum'
                }
            },
        ],
        StartTime=startTime,
        EndTime=endTime,
        ScanBy='TimestampAscending',
    )

    print("cloudwatch data: ", data)
    return data

cw = boto3.client("cloudwatch")
startTime = datetime.today()
ARN_T2 = "PLACEHOLDER_ARN"
ARN_LB = "PLACEHOLDER_ARN"
ARN_M4 = "PLACEHOLDER_ARN"

data_T2 = getCloudWatchMetrics(cw, startTime, ARN_T2, "cluster2", ARN_LB)
data_M4 = getCloudWatchMetrics(cw, startTime, ARN_M4, "cluster1", ARN_LB)