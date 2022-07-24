import boto3
from werkzeug.security import generate_password_hash, check_password_hash

dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

employees = dynamodb.create_table(
    TableName='Employees',
    KeySchema=[
        {
            'AttributeName': 'employeeName',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'employeeName',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

freePlaces = dynamodb.create_table(
    TableName='FreePlaces',
    KeySchema=[
        {
            'AttributeName': 'freePlacesKey',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'freePlacesKey',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

managers = dynamodb.create_table(
    TableName='Managers',
    KeySchema=[
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)
freePlaces.put_item(Item={'freePlacesKey': 'freePlaces', 'values': ['A2', 'A4', 'A5', 'B1', 'B4', 'B6', 'C1', 'C2', 'C3', 'C6', 'D2', 'D4', 'D5', 'D6']})

employees.put_item(Item={'employeeName': 'Andrew Nail', 'email': 'andrew.nail@iotcompany.com', 'role': 'Software Engineer', 'place': 'A1', 'absences': ['12-01', '18-01', '22-01', '27-02', '15-03', '11-04', '12-04', '02-06', '11-07', '13-07']})
employees.put_item(Item={'employeeName': 'John Iwine', 'email': 'john.iwine@iotcompany.com', 'role': 'Software Engineer', 'place': 'A3', 'absences': ['08-01', '15-01', '31-01', '11-03', '13-03', '02-04', '03-04', '08-06', '10-07', '13-07']})
employees.put_item(Item={'employeeName': 'Anthony Jitter', 'email': 'anthony.jitter@iotcompany.com', 'role': 'Backend Developer', 'place': 'A6', 'absences': ['15-01', '22-01', '03-04', '12-06', '12-07', '13-07', '21-07']})
employees.put_item(Item={'employeeName': 'Ted Affleck', 'email': 'ted.affleck@iotcompany.com', 'role': 'Backend Developer', 'place': 'B2', 'absences': ['15-02', '21-02', '18-03', '23-03', '07-04', '18-05', '21-05']})
employees.put_item(Item={'employeeName': 'Tony Stark', 'email': 'tony.stark@iotcompany.com', 'role': 'Backend Developer', 'place': 'B3', 'absences': ['17-03', '24-05', '11-06', '08-07']})
employees.put_item(Item={'employeeName': 'Phil Gallagher', 'email': 'phil.gallagher@iotcompany.com', 'role': 'Frontend Developer', 'place': 'B5', 'absences': ['23-01', '28-01', '15-03', '14-03', '08-05']})
employees.put_item(Item={'employeeName': 'Teddy Hogan', 'email': 'teddy.hogan@iotcompany.com', 'role': 'Frontend Developer', 'place': 'C4', 'absences': ['07-01', '12-05', '18-07']})
employees.put_item(Item={'employeeName': 'Holly Lotar', 'email': 'holly.lotar@iotcompany.com', 'role': 'Frontend Developer', 'place': 'C5', 'absences': ['03-03', '07-03', '15-04', '18-05', '19-05', '11-07']})
employees.put_item(Item={'employeeName': 'Jack McGregor', 'email': 'jack.mcgregor@iotcompany.com', 'role': 'Cloud Architect', 'place': 'D1', 'absences': ['06-05', '11-06', '24-06']})
employees.put_item(Item={'employeeName': 'Liam Sterling', 'email': 'liam.sterling@iotcompany.com', 'role': 'Cloud Architect', 'place': 'D3', 'absences': ['02-02', '02-04', '13-05', '19-06', '28-06']})

managers.put_item(Item={'managerName': 'Simon Flower', 'email': 'root@root.it', 'password': generate_password_hash('root')})

client = boto3.client('logs', endpoint_url="http://localhost:4566")
retention_period_in_days = 5

client.create_log_group(logGroupName='EmployeeAbsences')
client.create_log_group(logGroupName='EmailError')

client.put_retention_policy(logGroupName='EmployeeAbsences', retentionInDays=retention_period_in_days)
client.create_log_stream(logGroupName='EmployeeAbsences', logStreamName='EmailSent')
client.put_retention_policy(logGroupName='EmailError', retentionInDays=retention_period_in_days)
client.create_log_stream(logGroupName='EmailError', logStreamName='EmailSent')

print('Table', employees, 'created and populated successfully!')
print('Table', freePlaces, 'created and populated successfully!')
print('Table', managers, 'created and populated successfully!')
print('Cloudwatch stream EmployeeAbsences created successfully!')
print('Cloudwatch stream EmailError created successfully!')
