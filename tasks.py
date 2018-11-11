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

def postTask(request,tasks):
    request_json = request.get_json()
    child = people.find_one({'email':str.lower(request_json['payLoad']['childEmail'])},{'_id': False})
    stringName = child['firstName']+ ' '+ child['lastName']
    new_task = {
        'taskName': request_json['payLoad']['taskName'],
        'reward': request_json['payLoad']['reward'],
        'taskDeadline': request_json['payLoad']['taskDeadline'],
        'taskDescription': request_json['payLoad']['taskDescription'],
        'childEmail': str.lower(request_json['payLoad']['childEmail']),
        'childName': stringName,
        'complete': False,
        'verified': False,
        'dateCompleted': None,
        'familyName': child['familyName']
    }
    result1 = tasks.insert_one(new_task)
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

def completeTasks(request, tasks):
    request_json = request.get_json()
    tasksList = tasks.find({'childEmail':str.lower(request_json['payLoad']['email'])})
    for task in tasksList:
        if task['taskName'] == request_json['payLoad']['taskName']:
            tasks.update_one({'_id': task['_id']}, {"$set":{'complete': True}},upsert = False)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def verifyTasks(request, tasks):
    request_json = request.get_json()
    tasksList = tasks.find({'childEmail':str.lower(request_json['payLoad']['email'])})
    for task in taskList:
        if task['taskName'] == request_json['payLoad']['taskName']:
            tasks.update_one({'_id': task['_id']}, {"$set":{'verified': True}},upsert = False)
    response = jsonify([{
    }])
    response.status_code = 200
    return response
