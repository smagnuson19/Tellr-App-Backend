from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message

def getGoals(email, goals):
    goalList = goals.find({'email': str.lower(email)},{'_id': False})
    dictresponse = {}
    i = 0
    for goal in goalList:
        if goal['approved']==1:
            dictresponse[i]=goal
            i = i+1
    response = jsonify(dictresponse)
    print(dictresponse)
    response.status_code = 200
    return response

def postGoals(request, goals, people, notifications, mail, app):
    request_json = request.get_json()
    new_goal = {
        'name': request_json['payLoad']['name'],
        'value': float(request_json['payLoad']['value']),
        'email': fixEmail(request_json['payLoad']['email']),
        'description': request_json['payLoad']['description'],
        'image': request_json['payLoad']['image'],
        'approved': 0,
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
        'priority': realParent['notCounter'],
        'value': new_goal['value'],
        'read': False
    }
    notifications.insert_one(new_notification)
    current_priority = realParent['notCounter']
    people.update_one({'email': realParent['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
    result = goals.insert_one(new_goal)
    mstring = "Your child " + child['firstName'] + " has created a new goal: " + new_goal['name'] + ". Visit your tellrApp to learn more and to approve or send back their choice."
    for char in realParent['email']:
        if char == "@":
            with app.app_context():
                msg = Message("New Goal Created",
                                  sender="teller.notifications@gmail.com",
                                  recipients=[realParent['email']])
                msg.body = mstring
                mail.send(msg)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def finishGoal(request, people, goals, notifications, mail, app):
    request_json = request.get_json()
    child = people.find_one({'email': fixEmail(request_json['payLoad']['email'])})
    goalList = goals.find({'email': fixEmail(request_json['payLoad']['email'])})
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
        'priority': realParent['notCounter'],
        'value': redeemedGoal['value'],
        'read': False
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
        'priority': child['notCounter'],
        'value': redeemedGoal['value'],
        'read': False
    }
    notifications.insert_one(new_notification2)
    current_priority1 = child['notCounter']
    new_notification3 = {
        'email': child['email'],
        'accountType': 'Child',
        'notificationType': 'balanceChange',
        'notificationName': balanceDeduct,
        'description': newBalance,
        'senderName': child['firstName'],
        'senderEmail': child['email'],
        'priority': new_notification2['priority']+1,
        'value': balanceDeduct,
        'read': False
    }

    mstring = "Your child " + child['firstName'] + " has redeemed their goal: " + redeemedGoal['name'] + ". Visit your tellrApp to learn more!"
    for char in realParent['email']:
        if char == "@":
            with app.app_context():
                msg = Message("Goal Redeemed!",
                                  sender="teller.notifications@gmail.com",
                                  recipients=[realParent['email']])
                msg.body = mstring
                mail.send(msg)
    notifications.insert_one(new_notification3)
    people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority1+2}},upsert = False)

    response = jsonify([{
    }])
    response.status_code = 200
    return response

def approveGoal(request, goals, people, notifications, mail, app):
    request_json = request.get_json()
    child = people.find_one({'email': fixEmail(request_json['payLoad']['childEmail'])})
    goalList = goals.find({'email': fixEmail(request_json['payLoad']['childEmail'])})
    realGoal=None
    for goal in goalList:
        if goal['name'] == request_json['payLoad']['goalName']:
            realGoal = goal
            break
    if realGoal ==None:
        response = jsonify([{'Success': False
        }])
        response.status_code = 200
        return response
    goals.update_one({'_id': realGoal['_id']}, {"$set":{'approved': int(request_json['payLoad']['approved'])}},upsert = False)
    if int(request_json['payLoad']['approved']) == 1:
        status = 'Goal Approved'
    else:
        status = 'Goal Denied'

    parent = people.find_one({'email': fixEmail(request_json['payLoad']['senderEmail'])})

    new_notification1 = {
        'email': child['email'],
        'accountType': 'Child',
        'notificationType': 'goalApproval',
        'notificationName': realGoal['name'],
        'description': status,
        'senderName': parent['firstName'],
        'senderEmail': parent['email'],
        'priority': child['notCounter'],
        'value': realGoal['value'],
        'read': False
    }
    notifications.insert_one(new_notification1)
    current_priority = child['notCounter']
    people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)

    for char in child['email']:
        if char == "@":
            mstring = "Good news " + child['firstName'] + " ! Your goal for a " + realGoal['name'] + " has been approved! Visit your tellrApp to learn more. Remember that the quicker you do your tasks, the quicker you'll get your hands on the prize - see you soon!"
            with app.app_context():
                msg = Message("Goal Approved!!",
                                  sender="teller.notifications@gmail.com",
                                  recipients=[child['email']])
                msg.body = mstring
                mail.send(msg)
                
    response = jsonify([{
    }])
    response.status_code = 200
    return response
