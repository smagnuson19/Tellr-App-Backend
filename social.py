from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message
import datetime

def socialAdd(request, people, social):
    request_json = request.get_json()
    userEmail = fixEmail(request_json['payLoad']['email'])
    user = people.find_one({'email': userEmail}, {'_id': False})
    friendEmail = fixEmail(request_json['payLoad']['friend'])
    friend = people.find_one({'email': friendEmail}, {'_id': False})
    if friend == None:
        response = jsonify([{'Success': False, 'Error': "No user with given email found"
        }])
        response.status_code = 401
        return response

    new_notification = {
        'email': friendEmail,
        'accountType': 'Child',
        'notificationType': 'addRequest',
        'notificationName': user['firstName']+ " " +user['lastName'],
        'description': 'Social Add',
        'senderName': user['firstName'],
        'senderEmail': userEmail,
        'priority': friend['notCounter'],
        'value': 0,
        'read': False,
    }

    notifications.insert_one(new_notification)
    current_priority = friend['notCounter']
    people.update_one({'email': friendEmail}, {"$set":{'notCounter': current_priority+1}},upsert = False)

def socialAccept(request, people, social):
    request_json = request.get_json()
    senderEmail = request_json['payLoad']['friend']
    accepterEmail = request_json['payLoad']['email']

    sender = people.find_one({'email': senderEmail}, {'_id': False})
    accepter = people.find_one({'email': accepterEmail}, {'_id': False})
    senderFriends = sender['friends']
    accepterFriends = sender['friends']

    updatedSList = senderFriends.append(accepterEmail)
    updatedAList = accepterFriends.append(senderEmail)

    people.update_one({'email': senderEmail}, {"$set":{'friends': updatedSList}}, upsert = False)
    people.update_one({'email': accepterEmail}, {"$set":{'friends': updatedAList}}, upsert = False)

    new_notification = {
        'email': senderEmail,
        'accountType': 'Child',
        'notificationType': 'requestAccepted',
        'notificationName': accepter['firstName']+ " " + accepter['lastName'],
        'description': 'Social Add',
        'senderName': accepter['firstName'],
        'senderEmail': accepterEmail,
        'priority': sender['notCounter'],
        'value': 0,
        'read': False,
    }

    notifications.insert_one(new_notification)
    current_priority = sender['notCounter']
    people.update_one({'email': friendEmail}, {"$set":{'notCounter': current_priority+1}},upsert = False)

def getStats(email, people, social, tasks):
    user = people.find_one({'email': email}, {'_id': False})
    friendsList = user['friends']
    responseDict = {}
    now = datetime.datetime.now()
    for friendEmail in friendsList:
        friend = {}
        statsObj = social.find_one({'email': friendEmail}, {'_id': False})
        person = people.find_one({'email': friendEmail}, {'_id': False})
        tasksCompList= statsObj['tasksCompleted']
        index = len(tasksCompList) - 1
        current = tasksCompList[index]
        tasksCompleted = 0
        while ((now - current <= datetime.timedelta(days=7))):
            tasksCompleted += 1
            index -=1
            current = tasksCompList[index]
        friend['tasksCompletedWeek'] = tasksCompleted
        while ((now - current <= datetime.timedelta(days=30))):
            tasksCompleted += 1
            index -= 1
            current = tasksCompList[index]
        friend['tasksCompletedMonth'] = tasksComleted
        goalsCompList = statsObj['goalsCompleted']
        index = len(goalsCompList) - 1
        current = goalsCompList[index]
        goalsCompleted = 0
        while ((now - current <= datetime.timedelta(days=7))):
            goalsCompleted += 1
            index -= 1
            current = goalsCompList[index]
        friend['goalsCompletedWeek'] = goalsCompleted
        while ((now - current <= datetime.timedelta(days=30))):
            goalsCompleted +=1
            index -=1
            current = goalsCompList[index]
        friend['goalsCompletedWeek'] = goalsCompleted
        completionDeadlineList = statsObj['completionRate']
        index = len(completionDeadlineList) -1
        current = completionDeadlineList[index]
        tasksCompletedDeadline = 0
        while ((now - current <= datetime.timedelta(days=7)) and now > current):
            tasksCompletedDeadline +=1
            index -=1
            current = completionDeadlineList[index]
        totalTasksAssigned = get_total_tasks_week(tasks, friendEmail, now)
        taskCompleteRate = float(tasksCompletedDeadline/totalTasksAssigned)
        friend['taskCompletionRateWeek'] = taskCompleteRate
        while ((now - current <= datetime.timedelta(days=30)) and now > current):
            tasksCompletedDeadline +=1
            index -=1
            current = completionDeadlineList[index]
        totalTasksAssigned = get_total_tasks_month(tasks,friendEmail, now)
        taskCompleteRate = float(tasksCompletedDeadline/totalTasksAssigned)
        friend['taskCompletionRateMonth'] = taskCompleteRate
        friend['email'] = friendEmail
        friend['firstName'] = person['firstName']
        friend['lastName'] = person['lastName']
        responseDict[friendEmail] = friend
    response = jsonify(responseDict)
    response.status_code=200
    return response

def get_total_tasks_week(tasks, friendEmail, now):
    count = 0
    all = tasks.find({'email':str.lower(friendEmail)},{'_id': False})
    for task in all:
        if ((now - task['taskDeadline'] <= datetime.timedelta(days=7)) and now > task['taskDeadline']):
            count += 1
    return count

def get_total_tasks_month(tasks, friendEmail, now):
    count = 0
    all = tasks.find({'email':str.lower(friendEmail)},{'_id': False})
    for task in all:
        if ((now - task['taskDeadline'] <= datetime.timedelta(days=30)) and now > task['taskDeadline']):
            count += 1
    return count
