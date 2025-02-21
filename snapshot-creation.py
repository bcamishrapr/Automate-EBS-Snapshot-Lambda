import boto3
import collections
import datetime
 
ec = boto3.client('ec2')
 
def lambda_handler(event, context):
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup']},
        ]
    ).get(
        'Reservations', []
    )
  
  
  ## This is other way to achieve the same thing as described in below section.
  """
   response=ec2.describe_instances()
    instancelist = [] 
   for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"]) print (instancelist)
            
            """
  ###############################################################
  
  # This is sample code to understand below things, it is part of generator function
 """
    instances = sum(
     [
         [i*1 for i in range(3)]
         for r in range(4)
     ], [])
print (instances) 
"""
 
 ###TO CHECK THE FUNCTIONALITY OF SUM IN BELOW FUNCTION RUN BELOW CODE WITHOUT USING SUM and THEN USING SUM.
 
 """
instances = sum(
     [
         [i*1 for i in range(3)]
         for r in range(4)
     ], [])
print ("\nThis output is using sum\n")     
print (instances) 
#This is another code
print ("\nThis output is without using sum\n")
instances1 = [[i*1 for i in range(3)] 
for r in range(4)]
print (instances1)
"""
 
    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])
 
    print "Found %d instances that need backing up" % len(instances)
 
    to_tag = collections.defaultdict(list)
 
    for instance in instances:
        try:
            retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
        except IndexError:
            retention_days = 10
 
        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            print "Found EBS volume %s on instance %s" % (
                vol_id, instance['InstanceId'])
 
            snap = ec.create_snapshot(
                VolumeId=vol_id,
            )
 
            to_tag[retention_days].append(snap['SnapshotId'])
 
            print "Retaining snapshot %s of volume %s from instance %s for %d days" % (
                snap['SnapshotId'],
                vol_id,
                instance['InstanceId'],
                retention_days,
            )
 
 
    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        print "Will delete %d snapshots on %s" % (len(to_tag[retention_days]), delete_fmt)
        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
                {'Key': 'Name', 'Value': "LIVE-BACKUP"}
            ]
        )
