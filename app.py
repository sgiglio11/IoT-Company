from flask import Flask
from codes.CONFIG import DefaultConfig
import boto3
import datetime
from botocore.exceptions import ClientError
from werkzeug.security import check_password_hash
from flask import render_template, request, flash, redirect, url_for, session

app = Flask(__name__)
app.config['SECRET_KEY'] = DefaultConfig.FLASK_KEY

dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")
managers = dynamodb.Table('Managers')


@app.route("/home", methods=['GET', 'POST'])
def home():
    if ('user_in_session' not in  session):
        flash('You need to log in!', category='error')
        return redirect(url_for('login'))
    else:
        employees = dynamodb.Table('Employees').scan()["Items"]

        absences = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for user in employees:
            for absence in user['absences']:
                month = int(absence.split('-')[1])
                absences[month - 1] += 1
                thisMonth = int(datetime.datetime.now().strftime("%m"))
                thisMonthAbs = absences[thisMonth - 1]

        return render_template("index.html", employees = employees, absences = absences, percentage = int((thisMonthAbs/(thisMonth*30))*100))


@app.route('/', methods=['GET', 'POST'])
def login():
    employees = dynamodb.Table('Employees').scan()["Items"]
    if ('user_in_session' in  session):
        flash('You are already logged in!', category='success')
        return redirect(url_for('home'))
    if (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        try:
            user_found_dict = managers.get_item(Key={'email': email})
            if len(user_found_dict) > 1:
                user_found_dict = user_found_dict['Item']
                if check_password_hash(user_found_dict['password'], password):
                    flash('Logged in successfully!', category='success')
                    session['user_in_session'] = user_found_dict
                    return redirect(url_for('home', user=user_found_dict))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Username does not exist.', category='error')
        except ClientError as e:
            print('User not found!!')
            print(e.response['Error']['Message'])
    return render_template("login.html", employees = employees)


@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out with success!', category='success')
    return redirect(url_for('login'))


@app.route('/employees')
def employees():
    employees = dynamodb.Table('Employees').scan()["Items"]
    dateNow = str(datetime.datetime.now().strftime("%d-%m"))
    return render_template("employees.html", employees = employees, dateNow = dateNow)


@app.route('/updateEmployee', methods=['GET', 'POST'])
def updateEmployee():
    if (request.method == 'POST'):
        employeeName = str(request.form["nameInput"])
        email = str(request.form["emailInput"])
        role = str(request.form["roleInput"])
        place = str(request.form["placeInput"])

        employees = dynamodb.Table('Employees')

        oldPlace = str(employees.get_item(Key={'employeeName': employeeName})['Item']['place'])

        employees.update_item(Key={'employeeName': employeeName}, UpdateExpression="set #par1 = :email, #par2 = :role, #par3 = :place", ExpressionAttributeValues={':email': email, ':role': role, ':place': place}, ExpressionAttributeNames={'#par1': 'email', '#par2': 'role', '#par3': 'place'})

        freePlaces = dynamodb.Table('FreePlaces')
        values = freePlaces.get_item(Key={'freePlacesKey': 'freePlaces'})['Item']["values"]

        if place != oldPlace:
            values.remove(place)
            values.append(oldPlace)

        freePlaces.update_item(Key={'freePlacesKey': 'freePlaces'}, UpdateExpression="set #par1 = :values", ExpressionAttributeValues={':values': values}, ExpressionAttributeNames={'#par1': 'values'})

    flash('Changes done successfully!', category='success')
    return redirect(url_for('employees'))


@app.route('/employees/employeeDetails', methods=['GET', 'POST'])
def employeeDetails():
    if (request.method == 'POST'):
        employeeKey = request.form['View']
        employeeView = dynamodb.Table('Employees').get_item(Key={'employeeName': employeeKey})
        freePlaces = dynamodb.Table('FreePlaces').scan()["Items"]

        absences = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for absence in employeeView['Item']['absences']:
            month = int(absence.split('-')[1])
            absences[month-1] += 1;

        thisMonth = int(datetime.datetime.now().strftime("%m"))
        thisMonthAbs = absences[thisMonth-1]

        return render_template("employeeDetails.html", employeeView = employeeView["Item"], freePlaces = freePlaces[0]['values'], absences = absences, percentage = int(thisMonthAbs/30*100))


@app.route('/sendEmail', methods=['GET', 'POST'])
def sendEmail():
    if (request.method == 'POST'):
        CONFIG = DefaultConfig()
        client = boto3.client('ses', endpoint_url="http://localhost:4566")
        message = {
            'Subject': {
                'Data': str(request.form['subjectEmail']),
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': str(request.form['bodyEmail']),
                    'Charset': 'string'
                },
                'Html': {
                    'Data': 'This message body contains HTML formatting.',
                    'Charset': 'UTF-8'
                }
            }
        }
        response = client.send_email(
            Source=CONFIG.EMAIL_MANAGER,
            Destination={
                'ToAddresses': [
                    str(request.form['email']),
                ],
                'CcAddresses': [],
                'BccAddresses': []
            },
            Message=message
        )
        flash('Email sent successfully!', category='success')
        return redirect(url_for('employees'))


@app.route('/hireEmployees')
def hireEmployees():
    freePlaces = dynamodb.Table('FreePlaces').scan()["Items"]
    return render_template("hireEmployees.html", freePlaces = freePlaces[0]['values'])

@app.route('/hireEmployeeConfirm', methods=['GET', 'POST'])
def hireEmployeesConfirm():
    if (request.method == 'POST'):
        employeesTable = dynamodb.Table('Employees')

        employeeName = str(request.form["fullName"])
        email = str(request.form["email"])
        role = str(request.form["role"])
        place = str(request.form["freePlace"])

        employeesTable.put_item(Item={'employeeName': employeeName, 'email': email, 'role': role, 'place': place, 'absences': []})

        freePlaces = dynamodb.Table('FreePlaces')
        values = freePlaces.get_item(Key={'freePlacesKey': 'freePlaces'})['Item']["values"]
        values.remove(place)

        freePlaces.update_item(Key={'freePlacesKey': 'freePlaces'}, UpdateExpression="set #par1 = :values", ExpressionAttributeValues={':values': values}, ExpressionAttributeNames={'#par1': 'values'})

        flash('Employee hired successfully!', category='success')
        return redirect(url_for('employees'))


if __name__ == "__main__":
    app.run(debug=True)
