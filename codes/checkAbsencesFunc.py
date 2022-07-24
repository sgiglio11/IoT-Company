import datetime
import boto3
import time

from codes.CONFIG import DefaultConfig


def send_notifications(employeeName, place, absencesThisMonth, absences):
    CONFIG = DefaultConfig()
    client = boto3.client('ses', endpoint_url="http://localhost:4566")
    message = {
        'Subject': {
            'Data': 'Employee Problem',
            'Charset': 'UTF-8'
        },
        'Body': {
            'Text': {
                'Data': 'There is a problem with the employee ' + employeeName + ' sitting at the ' + place + ' desk who in this month has made more absences than allowed (' + str(absencesThisMonth) + ', ' + str(len(absences)) + ' absences from start of the year). \nWe urge you to carry out the necessary checks on the employee for the next month.',
                'Charset': 'string'
            },
            'Html': {
                'Data': 'This message body contains HTML formatting.',
                'Charset': 'UTF-8'
            }
        }
    }

    response = client.send_email(
        Source=CONFIG.EMAIL_PROTOTYPE,
        Destination={
            'ToAddresses': [
                CONFIG.EMAIL_MANAGER,
            ],
            'CcAddresses': [],
            'BccAddresses': []
        },
        Message=message
    )

    log_client = boto3.client('logs', endpoint_url="http://localhost:4566")

    log_event = {
        'logGroupName': 'EmployeeAbsences',
        'logStreamName': 'EmailSent',
        'logEvents': [
            {
                'timestamp': int(round(time.time() * 1000)),
                'message': str(message)
            },
        ],
    }

    log_client.put_log_events(**log_event)


def checkAbsences():
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
    employees = dynamodb.Table('Employees').scan()['Items']
    thisMonth = int(datetime.datetime.now().strftime("%m"))

    for user in employees:
        absencesThisMonth = 0
        for absence in user['absences']:
            month = int(absence.split('-')[1])
            if thisMonth == month:
                absencesThisMonth += 1
        if absencesThisMonth >= 7:
            send_notifications(user['employeeName'], user['place'], absencesThisMonth, user['absences'])


def lambda_handler(event, context):
    checkAbsences()


lambda_handler(None, None)