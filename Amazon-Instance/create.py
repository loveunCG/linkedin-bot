import boto3

region = 'us-east-1'
# instance = ['i-0688065841c95007e']

ec2 = boto3.resource('ec2')
ami_id = 'ami-015331952d15edeff'

# clone our Kale-Demo server

ec2.create_instances(ImageId=ami_id, MinCount=1, MaxCount=1)

# showing running instances

instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances:
    print(instance.id, instance.instance_type)
