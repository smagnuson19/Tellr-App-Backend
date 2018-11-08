from flask import Flask, request, jsonify

def getTasks(familyName,tasks):
    tasksList = tasks.find({'familyName':familyName},{'_id': False})
    dictresponse = {}
    i = 0
    for task in tasksList:
        dictresponse[i]=task
        i = i+1
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

def postTask(request,familyName,tasks):
    request_json = request.get_json()
    new_task = {
        'name': request_json['payLoad']['name'],
        'value': request_json['payLoad']['value'],
        'deadline': request_json['payLoad']['deadline'],
        'description': request_json['payLoad']['description'],
        'recEmail': request_json['payLoad']['recEmail'],
        'complete': False,
        'dateCompleted': None,
        'familyName':request_json['payLoad']['familyName']
    }
    result1 = tasks.insert_one(new_task)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def getTasksChild(email, tasks):
    tasksList = tasks.find({'recEmail':email},{'_id': False})
    dictresponse = {}
    i = 0
    for task in tasksList:
        dictresponse[i]=task
        i = i+1
    response = jsonify(dictresponse)
    response.status_code = 200
    return response
