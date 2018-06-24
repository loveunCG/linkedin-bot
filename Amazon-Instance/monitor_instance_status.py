from __future__ import print_function

import os
from datetime import datetime
import boto3

region = 'us-east-1'
# Enter your instances here: ex. ['X-XXXXXXXX', 'X-XXXXXXXX']
instanceIds = ['i-02edd8327c2bf6dd1']
        
try:
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances(InstanceIds=instanceIds)

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            print("The status of instanceid = '" + instance["InstanceId"] + "' is : " + instance["State"]["Name"])
except:
    print('Check failed!')
    raise
finally:
    print('Check completed at {}'.format(str(datetime.now())))