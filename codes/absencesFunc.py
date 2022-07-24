import boto3
import datetime
import json

sqs = boto3.client('sqs', endpoint_url='http://localhost:4566')
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")
employeesTable = dynamodb.Table('Employees')
employees = employeesTable.scan()['Items']


def lambda_handler(event, context):
    # queue = sqs.get_queue_by_name(QueueName=('proximity'))
    # while True:
    response = sqs.receive_message(QueueUrl='http://localhost:4566/000000000000/proximity')
    if 'Messages' in response:
        for message in response['Messages']:
            content = json.loads(message['Body'])
            for employee in employees:
                if content["device_place"] == employee["place"]:
                    absences = employee['absences']
                    absences.append(content['date'])
                    employeesTable.update_item(Key={'employeeName': employee['employeeName']},
                                          UpdateExpression="set #absences = :absences",
                                          ExpressionAttributeValues={':absences': absences},
                                          ExpressionAttributeNames={'#absences': 'absences'})
                    response = sqs.delete_message(QueueUrl='http://localhost:4566/000000000000/proximity',ReceiptHandle=message['ReceiptHandle'])
                    break


# lambda_handler(None, None)
