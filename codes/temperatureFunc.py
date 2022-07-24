import boto3
import datetime
import json

sqs = boto3.client('sqs', endpoint_url='http://localhost:4566')
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")


def lambda_handler(event, context):
    # while True:
    response = sqs.receive_message(QueueUrl='http://localhost:4566/000000000000/temperature')
    if 'Messages' in response:
        for message in response['Messages']:
            content = json.loads(message['Body'])
            if float(content['temperature']) >= 28:
                print("requests.get('https://enable-air-conditioning')")
                print("Air temperature is very high(" + str(
                    content['temperature']) + "° C), air conditioning enabling...")
                print("Air conditioning enabled successfully!")
            elif float(content['temperature']) <= 15:
                print("requests.get('https://enable-air-conditioning')")
                print(
                    "Air temperature is very low(" + str(content['temperature']) + "° C), air conditioning enabling...")
                print("Air conditioning enabled successfully!")
            else:
                print("Air temperature is ok.\t (" + str(content['temperature']) + "° C)")

            response = sqs.delete_message(QueueUrl='http://localhost:4566/000000000000/temperature',
                                          ReceiptHandle=message['ReceiptHandle'])

# lambda_handler(None, None)