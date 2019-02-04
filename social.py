from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message
import datetime
from copy import deepcopy

#Function for adding a friend in social leaderboard
def socialAdd(request, people, social, notifications):
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

    #Notification sent to friend being added
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

    notString = new_notification['notificationName'] + ' has invited you to connect on Tellr!'

    # Waiting for OneSignal account to test
    # send_notification(client, new_notification['friendEmail'], notString, 'Task Completion Verified!', push_notifications)

    response = jsonify([{
    }])
    response.status_code = 200
    return response

# Function for accepting friend requests
def socialAccept(request, people, social, notifications, push_notifications):
    request_json = request.get_json()
    senderEmail = request_json['payLoad']['friend']
    accepterEmail = request_json['payLoad']['email']

    #Updates the friend list of both the sender and the accepter
    sender = people.find_one({'email': senderEmail}, {'_id': False})
    accepter = people.find_one({'email': accepterEmail}, {'_id': False})
    senderFriends = deepcopy(sender['friends'])
    accepterFriends = deepcopy(accepter['friends'])
    print(senderFriends)
    print(accepterFriends)
    updatedSList = senderFriends + [accepterEmail]
    updatedAList = accepterFriends + [senderEmail]
    print(updatedSList)
    print(updatedAList)
    people.update_one({'email': senderEmail}, {"$set":{'friends': updatedSList}}, upsert = False)
    people.update_one({'email': accepterEmail}, {"$set":{'friends': updatedAList}}, upsert = False)

    #Notification sent to original requester
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
    people.update_one({'email': senderEmail}, {"$set":{'notCounter': current_priority+1}},upsert = False)

    notString = new_notification['notificationName'] + ' has accepted your friend request on Tellr!'

    # Waiting for OneSignal account to test
    # send_notification(client, new_notification['friendEmail'], notString, 'Task Completion Verified!', push_notifications)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def get_completed_task_number_graph(email, social):
    socialObject = social.find_one({'email': email}, {'_id': False})
    responseDict = {}
    for i in range(31):
        responseDict[i] = 0
    completedList = socialObject['tasksCompleted']
    quicksort(completedList)
    timeD = 0
    index = 0
    now = datetime.datetime.now()
    while timeD <= 31:
        tdeltamin = datetime.datetime.timedelta(days = timeD)
        tdeltamax = datetime.datetime.timedelta(days = timeD + 1)
        while (now - completedList[index]) >= tdeltamin and (now - completedList[index]) <= tdeltamax:
            index += 1
            responseDict[timeD] += 1
        timeD += 1
    response = jsonify([returnDict
        ])
    response.status_code = 200
    return response

def partition(the_list, p, r):
    i = p - 1              # i demarcates the end of the sublist containing values <= pivot.
    j = p                  # j demarcates end of sublist containing values > pivot.
    pivot = the_list[r]    # Pivot will store value of sublist's last item.
    while j < r:
        if the_list[j] > pivot:
            j += 1         # Increment j.
        elif the_list[j] <= pivot:
            i += 1         # Increment i.
            the_list[i], the_list[j] = the_list[j], the_list[i]
            j += 1
    the_list[r], the_list[i + 1] = the_list[i + 1], the_list[r]
    return i + 1

# Sort the_list[p ... r], using quick sort.
def quicksort_time(the_list, p = 0, r = None):
    # If using the default parameters, sort the entire list.
    if r == None:
        r = len(the_list) - 1
    # Base case: If sublist has fewer than 2 items... then do nothing. No code required!
    if p < r:
        q = partition(the_list, p, r)  # Locates pivot item, since partition returns its index.
        quicksort_time(the_list, p, q - 1)  # Quicksort sublist from p to q (exclusive).
        quicksort_time(the_list, q + 1, r)  # Quicksort sublist from one past q to r (inclusive).
    return the_list

#Function for getting social statistics for leaderboard
def getStats(email, people, social, tasks):
    user = people.find_one({'email': email}, {'_id': False})
    print(user)
    friendsList = user['friends']
    responseDict = {}
    now = datetime.datetime.now()
    #Find the list first, then count the number of tasks completed/goals completed in the past week/month
    for friendEmail in friendsList:
        friend = {}
        statsObj = social.find_one({'email': friendEmail}, {'_id': False})
        person = people.find_one({'email': friendEmail}, {'_id': False})

        tasksCompleted = 0
        tasksCompList= statsObj['tasksCompleted']
        index = len(tasksCompList) - 1
        if index >=0:
            current = tasksCompList[index]
            while ((now - current <= datetime.timedelta(days=7))): #last week
                tasksCompleted += 1
                index -=1
                if index == -1:
                    break
                current = tasksCompList[index]
        friend['tasksCompletedWeek'] = tasksCompleted
        if index >=0:
            while ((now - current <= datetime.timedelta(days=30))): #last month
                tasksCompleted += 1
                index -= 1
                if index == -1:
                    break
                current = tasksCompList[index]
        friend['tasksCompletedMonth'] = tasksCompleted
        goalsCompList = statsObj['goalsCompleted']
        index = len(goalsCompList) - 1
        goalsCompleted = 0
        if index >=0:
            current = goalsCompList[index]
            while ((now - current <= datetime.timedelta(days=7))):
                goalsCompleted += 1
                index -= 1
                if index == -1:
                    break
                current = goalsCompList[index]
        friend['goalsCompletedWeek'] = goalsCompleted
        if index >=0:
            while ((now - current <= datetime.timedelta(days=30))):
                goalsCompleted +=1
                index -=1
                if index == -1:
                    break
                current = goalsCompList[index]
        friend['goalsCompletedMonth'] = goalsCompleted
        completionDeadlineList = statsObj['completionRate']
        index = len(completionDeadlineList) -1
        tasksCompletedDeadline = 0
        #For completion rate, find the total number of tasks assigned in past month/week,
        #then the number of those that are completed
        if index >=0:
            current = completionDeadlineList[index]
            while ((now - current <= datetime.timedelta(days=7)) and now > current):
                tasksCompletedDeadline +=1
                index -=1
                if index == -1:
                    break
                current = completionDeadlineList[index]
        totalTasksAssigned = get_total_tasks_week(tasks, friendEmail, now)
        if totalTasksAssigned == 0:
            taskCompleteRate = 0
        else:
            #Send rate as float
            taskCompleteRate = float(tasksCompletedDeadline/totalTasksAssigned)
        friend['taskCompletionRateWeek'] = taskCompleteRate
        if index >=0:
            while ((now - current <= datetime.timedelta(days=30)) and now > current):
                tasksCompletedDeadline +=1
                index -=1
                if index == -1:
                    break
                current = completionDeadlineList[index]
        totalTasksAssigned = get_total_tasks_month(tasks,friendEmail, now)
        if totalTasksAssigned == 0:
            taskCompleteRate = 0
        else:
            taskCompleteRate = float(tasksCompletedDeadline/totalTasksAssigned)
        friend['taskCompletionRateMonth'] = taskCompleteRate
        friend['email'] = friendEmail
        friend['firstName'] = person['firstName']
        friend['lastName'] = person['lastName']
        responseDict[friendEmail] = friend
    print(responseDict)
    response = jsonify(responseDict)
    response.status_code=200
    return response

#Helper function to get the total number of tasks in a week
def get_total_tasks_week(tasks, friendEmail, now):
    count = 0
    all = tasks.find({'email':str.lower(friendEmail)},{'_id': False})
    for task in all:
        if ((now - task['taskDeadline'] <= datetime.timedelta(days=7)) and now > task['taskDeadline']):
            count += 1
    return count

#Helper function to get the total number of tasks in a month
def get_total_tasks_month(tasks, friendEmail, now):
    count = 0
    all = tasks.find({'email':str.lower(friendEmail)},{'_id': False})
    for task in all:
        if ((now - task['taskDeadline'] <= datetime.timedelta(days=30)) and now > task['taskDeadline']):
            count += 1
    return count
