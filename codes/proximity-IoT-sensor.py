import boto3
import datetime
import random

sqs = boto3.resource('sqs', endpoint_url='http://localhost:4566')
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")
today = str(datetime.datetime.now().strftime("%d-%m"))
todayComplete = str(datetime.datetime.now())

employees = dynamodb.Table('Employees').scan()['Items']
places = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6']
placesOccupied = []


def proximity():
    for employee in employees:
        placesOccupied.append(employee['place'])

    for place in places:
        if place in placesOccupied:
            queue = sqs.get_queue_by_name(QueueName='proximity')

            if random.random() < 0.10:
                errorQueue = sqs.get_queue_by_name(QueueName="errors")
                errorMsg = '{"device_place": "%s","error_date": "%s"}' % (place, todayComplete)
                print(errorMsg)
                errorQueue.send_message(MessageBody=errorMsg)
            else:
                isAbsent = random.random()
                if isAbsent > 0.8:
                    msg = '{"device_place": "%s","date": "%s","employeeState": "absent"}' % (place, today)
                    print(msg)
                    queue.send_message(MessageBody=msg)


proximity()
