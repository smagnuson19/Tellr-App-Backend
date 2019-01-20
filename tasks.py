from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message
from datetime import datetime

def getTasks(familyName,tasks):
    tasksList = tasks.find({'familyName':str.lower(familyName)},{'_id': False})
    dictresponse = {}
    i = 0
    for task in tasksList:
        dictresponse[i]=task
        i = i+1
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

def postTask(request,tasks, people, notifications, mail, app):
    request_json = request.get_json()
    print(request_json)
    if request_json['payLoad']['childEmail'] == '':
        response = jsonify([{'Success': False,
        'Error': 'No children selected'
        }])
        response.status_code = 401
        return response
    child = people.find_one({'email':fixEmail(request_json['payLoad']['childEmail'])},{'_id': False})
    stringName = child['firstName']+ ' '+ child['lastName']

    date_time_str = request_json['payLoad']['taskDeadline']
    datelist = date_time_str.split()
    realstr = datelist[0][:3] + " " + datelist[1][:-2] + " " + datelist[2][:-1]+ " " + datelist[3]
    date_time_obj = datetime.datetime.strptime(realstr, '%b %d %Y %I:%M%p')

    new_task = {
        'taskName': request_json['payLoad']['taskName'],
        'reward': float(request_json['payLoad']['reward']),
        'taskDeadline': date_time_obj,
        'taskDescription': request_json['payLoad']['taskDescription'],
        'childEmail': fixEmail(request_json['payLoad']['childEmail']),
        'senderEmail': fixEmail(str.lower(request_json['payLoad']['senderEmail'])),
        'childName': stringName,
        'complete': False,
        'verified': False,
        'dateCompleted': None,
        'familyName': child['familyName'],
        'alert': False
    }

    result1 = tasks.insert_one(new_task)
    parent = people.find_one({'email': new_task['senderEmail']},{'_id': False})
    sName = parent['firstName']+ ' '+ parent['lastName']

    now =datetime.datetime.now()
    if (new_task['taskDeadline']-now) < datetime.timedelta(hours=24):
        display = True
    else:
        display = False

    new_notification = {
        'email': child['email'],
        'accountType': 'Child',
        'notificationType': 'newTask',
        'notificationName': new_task['taskName'],
        'description': new_task['taskDescription'],
        'senderName': sName,
        'senderEmail': parent['email'],
        'priority': child['notCounter'],
        'value': new_task['reward'],
        'read': False,
        'deadline': datetime.datetime.strftime(new_task['taskDeadline'], '%b %d %Y %I:%M%p'),
        'displayRed': display
    }
    notifications.insert_one(new_notification)
    current_priority = child['notCounter']
    people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
    # mstring = "You've got money! (almost...) Your parents have posted a new task: " + new_task['taskName'] + "! Make sure to check out your tellrApp for details and complete this task before the deadline passes!"
    # for char in child['email']:
    #     if char == "@":
    #         with app.app_context():
    #             msg = Message("You've Got a New Money Opportunity!",
    #                               sender="teller.notifications@gmail.com",
    #                               recipients=[child['email']])
    #             msg.body = mstring
    #             mail.send(msg)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def getTasksChild(email, tasks):
    tasksList = tasks.find({'childEmail':str.lower(email)},{'_id': False})
    dictresponse = {}
    i = 0
    for task in tasksList:
        task['taskDeadline'] = str(task['taskDeadline'])
        dictresponse[i]=task
        i = i+1
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

def completeTask(request, tasks, notifications, people, mail, app):
    request_json = request.get_json()
    child = people.find_one({'email':fixEmail(request_json['payLoad']['email'])})
    stringName = child['firstName']+ ' '+ child['lastName']
    tasksList = tasks.find({'childEmail':fixEmail(str.lower(request_json['payLoad']['email']))})
    for task in tasksList:
        if task['taskName'] == request_json['payLoad']['taskName']:
            actualT = task
            tasks.update_one({'_id': task['_id']}, {"$set":{'complete': True}},upsert = False)
            parent = people.find_one({'email':str.lower(task['senderEmail'])})
            new_notification = {
                'email': task['senderEmail'],
                'accountType': 'Parent',
                'notificationType': 'taskComplete',
                'notificationName': task['taskName'],
                'description': task['taskDescription'],
                'senderName': stringName,
                'senderEmail': child['email'],
                'priority': parent['notCounter'],
                'value': task['reward'],
                'read': False
            }
            print(new_notification)
            print(task)
            notifications.insert_one(new_notification)
            current_priority = parent['notCounter']
            people.update_one({'email': parent['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
    #
    # mstring = "Your child has completed the task: " + actualT['taskName'] + ". Please visit tellrApp to see details and to verify!"
    # for char in task['senderEmail']:
    #     if char == "@":
    #         with app.app_context():
    #             msg = Message("Task Completed",
    #                               sender="teller.notifications@gmail.com",
    #                               recipients=[task['senderEmail']])
    #             msg.body = mstring
    #             mail.send(msg)

    response = jsonify([{
    }])
    response.status_code = 200
    return response

def verifyTask(request, tasks, notifications, people, mail, app):
    request_json = request.get_json()
    child = people.find_one({'email':fixEmail(request_json['payLoad']['email'])})
    tasksList = tasks.find({'childEmail': fixEmail(request_json['payLoad']['email'])})
    if request_json['payLoad']['verify'] == True:
        for task in tasksList:
            if task['taskName'] == request_json['payLoad']['taskName']:
                actualT = task
                tasks.update_one({'_id': task['_id']}, {"$set":{'verified': True}},upsert = False)
                parent = people.find_one({'email':fixEmail(task['senderEmail'])})
                stringName = parent['firstName']+ ' '+ parent['lastName']
                new_notification={
                    'email': child['email'],
                    'accountType': 'Child',
                    'notificationType': 'taskVerified',
                    'notificationName': task['taskName'],
                    'description': task['taskDescription'],
                    'senderName': parent['firstName'],
                    'senderEmail': parent['email'],
                    'priority': child['notCounter'],
                    'value': task['reward'],
                    'read': False
                }
                notifications.insert_one(new_notification)
                current_priority = child['notCounter']
                new_balance = child['balance'] + float(task['reward'])
                people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
                people.update_one({'email': child['email']}, {"$set":{'balance': new_balance}},upsert = False)
                break

        # mstring = "Awesome work " + child['firstName'] + ", your completion of the task: " + actualT['taskName'] + " has been verified. See your tellrApp for your updated balanc !"
        # print("test")
        # for char in child['email']:
        #     if char == "@":
        #         with app.app_context():
        #             msg = Message("Cha Ching!",
        #                               sender="teller.notifications@gmail.com",
        #                               recipients=[child['email']])
        #             msg.body = mstring
        #             mail.send(msg)
        response = jsonify([{
        }])
        response.status_code = 200
        return response
    else:
        for task in tasksList:
            if task['taskName'] == request_json['payLoad']['taskName']:
                tasks.update_one({'_id': task['_id']}, {"$set":{'complete': False}},upsert = False)
                parent = people.find_one({'email':fixEmail(task['senderEmail'])})
                new_notification={
                    'email': child['email'],
                    'accountType': 'Child',
                    'notificationType': 'taskUnverified',
                    'notificationName': task['taskName'],
                    'description': task['taskDescription'],
                    'senderName': parent['firstName'],
                    'senderEmail': parent['email'],
                    'priority': child['notCounter'],
                    'value': task['reward'],
                    'read': False
                }
                notifications.insert_one(new_notification)
                current_priority = child['notCounter']
                people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
                break
        response = jsonify([{
        }])
        response.status_code = 200
        return response
