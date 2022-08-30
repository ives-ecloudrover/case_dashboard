from importlib.resources import path
import boto3
import json
import os
import csv

class SaveCSV(object):
    def save(self,keyword_list,path,item):
        try:
            if not os.path.exists(path):
                with open(path,"w",newline='',encoding='utf-8') as csvfile:
                    write=csv.DictWriter(csvfile,fieldnames=keyword_list)
                    write.writeheader()
            with open(path,"a",newline='',encoding='utf-8') as csvfile:
                write=csv.DictWriter(csvfile,fieldnames=keyword_list)
                write.writerow(item)
                print("write success")
        except Exception as e:
            print("write error==>",e)
            with open("error.txt","w") as f:
                f.write(json.dumps(item)+",\n")
        
accounts=[
    'arn:aws:iam::224886979707:role/SupportECR',
    'arn:aws:iam::366935765673:role/SupportECR'
]

def desribe_case(support_client):
    response = support_client.describe_cases(
        includeCommunications=False
    )
    print(response)
def listBucket(support_resources):
    for bucket in support_resources.buckets.all():
        print(bucket.name)
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
    
    
    support_resources=boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN
    )
    return support_resources
def main():
    for account in accounts:
        try:
            support_resources=get_sts_token(account=account)
            listBucket(support_resources=support_resources)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    #main()
    path = "test1.csv"
    item={
        'num':60,
        'keyword':'软件开发'
    }
    item_list=[
        "account",
        "displayId",
        "subject",
        "status",
        "serviceCode",
        "categoryCode",
        "severityCode",
        "timeCreated"
    ]
    s=SaveCSV()
    for i in range(3):
        s.save(item_list,path,item)