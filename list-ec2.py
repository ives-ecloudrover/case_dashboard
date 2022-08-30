import boto3
import botostubs
import csv
import pandas as pd
import numpy as np

client=boto3.client('support') # type: botostubs.Support
s3=boto3.client('s3') #type: botostubs.S3

#account info
accounts=[
    'arn:aws:iam::009782398905:role/TestECR',
    'arn:aws:iam::410948239121:role/TestECR',
    'arn:aws:iam::887455658500:role/TestECR'
]
#Obtained token by Switch role
def get_sts_token(account):
    sts_client = boto3.client('sts')
    role_session_name = "cross_cases_session"
    assumed_role_object=sts_client.assume_role(
        RoleArn=account,
        RoleSessionName=role_session_name
    )
    ACCESS_KEY    = assumed_role_object['Credentials']['AccessKeyId']
    SECRET_KEY    = assumed_role_object['Credentials']['SecretAccessKey']
    SESSION_TOKEN = assumed_role_object['Credentials']['SessionToken']
    
    support_resources=boto3.client(
        'ec2',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN
    )
    currentAccount=account[13:25]
    #print(support_resources.describe_instances())
    return support_resources,currentAccount


def main():
    
    f = open('./case_list.csv', 'a+', newline='\n', encoding='utf-8')
    csv_writer = csv.writer(f)
    csv_reader=csv.reader(f)
    # csv_writer.writerow(['account_id', 'instance_id', 'instance_state', 'instance_type','avaiability_zone', 'public_ipv4', 'launch_time'])
    data=pd.read_csv("./case_list.csv")
    col_1=data["instance_id"]
    instance_data=np.array(col_1)
    for account in accounts:
        try:
            support_resources=get_sts_token(account=account)
            instances_res=support_resources[0].describe_instances()
            num_of_keys = len(instances_res['Reservations'])
            for num in range(0, num_of_keys):
                num_of_ins = len(instances_res['Reservations'][num]['Instances'])
                for i in range(0, num_of_ins):
                    InstanceId = instances_res['Reservations'][num]['Instances'][i]['InstanceId']
                    InstanceState=instances_res['Reservations'][num]['Instances'][i]['State']['Name']
                    InstanceType = instances_res['Reservations'][num]['Instances'][i]['InstanceType']
                    AvaiabilityZone=instances_res['Reservations'][num]['Instances'][i]['Placement']['AvailabilityZone']
                    PublicIpAddress=instances_res['Reservations'][num]['Instances'][i]['PublicIpAddress']
                    LaunchTime=instances_res['Reservations'][num]['Instances'][i]['LaunchTime']
                    
                    if InstanceId not in instance_data:
                        row_csv = (support_resources[1],InstanceId,InstanceState,InstanceType,AvaiabilityZone,PublicIpAddress,LaunchTime)
                        csv_writer.writerow(row_csv)
        except Exception as e:
            print(e)
    f.close()
    s3.upload_file("./case_list.csv","ives-ecloudrover","casefile/case_list.csv")

if __name__ == '__main__':
    
    main()
    ''' for caseinfo in responses['cases']:
        account=12345,
        displayId=caseinfo['displayId'],
        subject=caseinfo['subject'],
        status=caseinfo['status'],
        serviceCode=caseinfo['serviceCode'],
        categoryCode=caseinfo['categoryCode'],
        severityCode=caseinfo['severityCode'],
        timeCreated=caseinfo['timeCreated']'''