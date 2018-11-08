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

def postGoals(request, email, goals):
    request_json = request.get_json()
    new_goal = {
        'Name': request_json['goalInfo']['Name'],
        'Prize': request_json['goalInfo']['Prize'],
        'email': str.lower(email),
        'Description': request_json['goalInfo']['Description']
    }
    result = goals.insert_one(new_goal)
