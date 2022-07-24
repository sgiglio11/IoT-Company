import boto3
import datetime
import random

sqs = boto3.resource('sqs', endpoint_url='http://localhost:4566')
today = str(datetime.datetime.now().strftime("%d-%m"))


def air_temperature():
    temperature = round(random.uniform(8.0, 35.0), 2)
    queue = sqs.get_queue_by_name(QueueName='temperature')
    msg = '{"temperature": "%f","date": "%s"}' % (temperature, today)
    print('-- Air temperature of today ' + today + ' sended!!!')
    queue.send_message(MessageBody=msg)


air_temperature()