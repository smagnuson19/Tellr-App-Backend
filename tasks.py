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
    new_task = {
        'taskName': request_json['payLoad']['taskName'],
        'reward': request_json['payLoad']['reward'],
        'taskDeadline': request_json['payLoad']['taskDeadline'],
        'taskDescription': request_json['payLoad']['taskDescription'],
        'childEmail': str.lower(request_json['payLoad']['childEmail']),
        'complete': False,
        'dateCompleted': None,
        'familyName':str.lower(request_json['payLoad']['familyName'])
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
