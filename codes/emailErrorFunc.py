import boto3
import time
import json

from codes.CONFIG import DefaultConfig

CONFIG = DefaultConfig()
clientSQS = boto3.client('sqs', endpoint_url='http://localhost:4566')
clientSES = boto3.client('ses', endpoint_url="http://localhost:4566")


def lambda_handler(event, context):
    while True:
        response = clientSQS.receive_message(QueueUrl='http://localhost:4566/000000000000/errors')
        if 'Messages' in response:
            for content in response['Messages']:
                msgBody = json.loads(content['Body'])
                device_place = msgBody['device_place']
                error_date = msgBody['error_date']

                dataMessage = f"<b>device_place</b>: {str(device_place)}<br>" \
                              f"<b>error_date</b>: {str(error_date)}<br>" \

                message = {
                    'Subject': {
                        'Data': 'IoT-Company Error',
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': dataMessage,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': 'This message body contains HTML formatting.',
                            'Charset': 'UTF-8'
                        }
                    }
                }

                response = clientSES.send_email(
                    Source=CONFIG.EMAIL_MANAGER,
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
                    'logGroupName': 'EmailError',
                    'logStreamName': 'EmailSent',
                    'logEvents': [
                        {
                            'timestamp': int(round(time.time() * 1000)),
                            'message': str(message)
                        },
                    ],
                }

                log_client.put_log_events(**log_event)

                print("The message is corrected sent to " + CONFIG.EMAIL_MANAGER)

                response = clientSQS.delete_message(QueueUrl='http://localhost:4566/000000000000/errors', ReceiptHandle=content['ReceiptHandle'])

lambda_handler(None, None)
