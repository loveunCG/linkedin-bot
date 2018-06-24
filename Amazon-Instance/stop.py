import boto3
# Enter the region your instances are in. Include only the region without specifying Availability Zone; e.g., 'us-east-1'
region = 'us-east-1'
# Enter your instances here: ex. ['X-XXXXXXXX', 'X-XXXXXXXX']
instances = ['i-02edd8327c2bf6dd1']

ec2 = boto3.client('ec2', region_name=region)
ec2.stop_instances(InstanceIds=instances)
print ('stopped your instances: ' + str(instances))