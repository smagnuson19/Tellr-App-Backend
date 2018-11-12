from flask import Flask, request, jsonify

def getGoals(email, goals):
    goalList = goals.find({'email': str.lower(email)},{'_id': False})
    dictresponse = {}
    i = 0
    for goal in goalList:
        dictresponse[i]=goal
        i = i+1
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

def postGoals(request, goals, people, notifications):
    request_json = request.get_json()
    new_goal = {
        'name': request_json['payLoad']['name'],
        'value': request_json['payLoad']['value'],
        'email': str.lower(email),
        'description': request_json['payLoad']['description'],
        'image': request_json['payLoad']['image']
    }
    result = goals.insert_one(new_goal)
