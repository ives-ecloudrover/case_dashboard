from unittest import result
import boto3
import botostubs
import pymysql

client = boto3.client('support')  # type: botostubs.Support

# define database connection info
connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='123456',
                             db='test',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
#create cursor
cursor = connection.cursor()

#account info
accounts = [
    'arn:aws:iam::224886979707:role/SupportECR',
    'arn:aws:iam::366935765673:role/SupportECR'
]


#Obtained token by Switch role
def get_sts_token(account):
    sts_client = boto3.client('sts')
    role_session_name = "cross_cases_session"
    assumed_role_object = sts_client.assume_role(
        RoleArn=account, RoleSessionName=role_session_name)
    ACCESS_KEY = assumed_role_object['Credentials']['AccessKeyId']
    SECRET_KEY = assumed_role_object['Credentials']['SecretAccessKey']
    SESSION_TOKEN = assumed_role_object['Credentials']['SessionToken']

    support_resources = boto3.resource('s3',
                                       aws_access_key_id=ACCESS_KEY,
                                       aws_secret_access_key=SECRET_KEY,
                                       aws_session_token=SESSION_TOKEN)
    currentAccount = account[13:25]
    return support_resources, currentAccount


def queryCaseId(conn):
    cursor = conn.cursor()
    cursor.execute("select s3_name from s3")
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    return result


#TEST list bucket
def listBucket(support_resources):
    results = queryCaseId(connection)
    result_list = []
    for record in results:
        result_list.append(record['s3_name'])
    for bucket in support_resources[0].buckets.all():
        value = (support_resources[1], bucket.name)
        if bucket.name not in result_list:
            return value


def main():
    for account in accounts:
        try:
            support_resources = get_sts_token(account=account)
            value = listBucket(support_resources=support_resources)
            # print(value)
            # if value is not None:
            #     sql_insert="insert into s3 values (%s,%s)"
            #     cursor.execute(sql_insert,value)
            #     connection.commit()
        except Exception as e:
            print(e)


# responses=client.describe_cases(
#     afterTime='2022-06-24T00:00:00Z',
#     includeCommunications=False
# )

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