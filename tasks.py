from flask import Flask, request, jsonify

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

def postTask(request,tasks, people, notifications):
    request_json = request.get_json()
    child = people.find_one({'email':str.lower(request_json['payLoad']['childEmail'])},{'_id': False})
    stringName = child['firstName']+ ' '+ child['lastName']
    new_task = {
        'taskName': request_json['payLoad']['taskName'],
        'reward': request_json['payLoad']['reward'],
        'taskDeadline': request_json['payLoad']['taskDeadline'],
        'taskDescription': request_json['payLoad']['taskDescription'],
        'childEmail': str.lower(request_json['payLoad']['childEmail']),
        'senderEmail': str.lower(request_json['payLoad']['senderEmail']),
        'childName': stringName,
        'complete': False,
        'verified': False,
        'dateCompleted': None,
        'familyName': child['familyName']
    }
    result1 = tasks.insert_one(new_task)
    parent = people.find_one({'email':new_task['senderEmail']},{'_id': False})
    sName = parent['firstName']+ ' '+ parent['lastName']
    new_notification = {
        'email': child['email'],
        'accountType': 'Child',
        'notificationType': 'newTask',
        'notificationName': new_task['taskName'],
        'description': new_task['taskDescription'],
        'senderName': sName,
        'senderEmail': parent['email'],
        'priority': child['notCounter']
    }
    notifications.insert_one(new_notification)
    current_priority = child['notCounter']
    people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def getTasksChild(email, tasks):
    tasksList = tasks.find({'recEmail':str.lower(email)},{'_id': False})
    dictresponse = {}
    i = 0
    for task in tasksList:
        dictresponse[i]=task
        i = i+1
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

def completeTasks(request, tasks, notifications, people):
    request_json = request.get_json()
    child = people.find_one({'email':str.lower(request_json['payLoad']['email'])})
    stringName = child['firstName']+ ' '+ child['lastName']
    tasksList = tasks.find({'childEmail':str.lower(request_json['payLoad']['email'])})
    for task in tasksList:
        if task['taskName'] == request_json['payLoad']['taskName']:
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
                'priority': parent['notCounter']
            }
            notifications.insert_one(new_notification)
            current_priority = parent['notCounter']
            people.update_one({'email': parent['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
            break
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def verifyTasks(request, tasks, notifications, people):
    request_json = request.get_json()
    child = people.find_one({'email':str.lower(request_json['payLoad']['email'])})
    tasksList = tasks.find({'childEmail':str.lower(request_json['payLoad']['email'])})
    for task in taskList:
        if task['taskName'] == request_json['payLoad']['taskName']:
            tasks.update_one({'_id': task['_id']}, {"$set":{'verified': True}},upsert = False)
            parent = people.find_one({'email':str.lower(task['senderEmail'])})
            stringName = parent['firstName']+ ' '+ parent['lastName']
            new_notification={
                'email': child['email'],
                'accountType': 'Child',
                'notificationType': 'taskVerified',
                'notificationName': task['taskName'],
                'description': task['taskDescription'],
                'senderName': stringName,
                'senderEmail': parent['email'],
                'priority': child['notCounter']
            }
            notifications.insert_one(new_notification)
            current_priority = child['notCounter']
            people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
            break
    response = jsonify([{
    }])
    response.status_code = 200
    return response
