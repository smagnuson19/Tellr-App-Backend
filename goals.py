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
        'value': float(request_json['payLoad']['value']),
        'email': str.lower(request_json['payLoad']['email']),
        'description': request_json['payLoad']['description'],
        'image': request_json['payLoad']['image'],
        'redeemed': False
    }
    child = people.find_one({'email':new_goal['email']})
    parents = people.find({'familyName': child['familyName']})
    for parent in parents:
        if parent['accountType']=='Parent':
            realParent = parent
            break
    new_notification = {
        'email': realParent['email'],
        'accountType': 'Parent',
        'notificationType': 'newGoal',
        'notificationName': new_goal['name'],
        'description': new_goal['description'],
        'senderName': child['firstName'],
        'senderEmail': child['email'],
        'priority': realParent['notCounter']
    }
    notifications.insert_one(new_notification)
    current_priority = realParent['notCounter']
    people.update_one({'email': realParent['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)

    result = goals.insert_one(new_goal)

def finishGoal(request, people, goals, notifications):
    request_json = request.get_json()
    child = people.find_one({'email': str.lower(request_json['payLoad']['email'])})
    goalList = goals.find({'email': str.lower(request_json['payLoad']['email'])})
    for goal in goalList:
        if goal['name'] == request_json['payLoad']['goalName']:
            redeemedGoal = goal
            break
    goals.update_one({'_id': redeemedGoal['_id']}, {"$set":{'redeemed': True}},upsert = False)
    balanceDeduct = redeemedGoal['value']
    currentBalance = child['balance']
    newBalance = currentBalance-balanceDeduct
    people.update_one({'email': child['email']},{"$set":{'balance': newBalance}},upsert = False)
    parents = people.find({'familyName': child['familyName']})
    for parent in parents:
        if parent['accountType']=='Parent':
            realParent = parent
            break
    new_notification1 = {
        'email': realParent['email'],
        'accountType': 'Parent',
        'notificationType': 'goalComplete',
        'notificationName': redeemedGoal['name'],
        'description': redeemedGoal['description'],
        'senderName': child['firstName'],
        'senderEmail': child['email'],
        'priority': realParent['notCounter']
    }
    notifications.insert_one(new_notification1)
    current_priority = realParent['notCounter']
    people.update_one({'email': realParent['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
    new_notification2 = {
        'email': child['email'],
        'accountType': 'Child',
        'notificationType': 'goalComplete',
        'notificationName': redeemedGoal['name'],
        'description': redeemedGoal['description'],
        'senderName': child['firstName'],
        'senderEmail': child['email'],
        'priority': child['notCounter']
    }
    notifications.insert_one(new_notification2)
    current_priority1 = child['notCounter']
    people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority1+1}},upsert = False)
    new_notification3 = {
        'email': child['email'],
        'accountType': 'Child',
        'notificationType': 'balanceChange',
        'notificationName': balanceDeduct,
        'description': newBalance,
        'senderName': child['firstName'],
        'senderEmail': child['email'],
        'priority': child['notCounter']
    }
    notifications.insert_one(new_notification3)
    current_priority2 = child['notCounter']
    people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority2+1}},upsert = False)
