from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message
import datetime
from copy import deepcopy
from push import *

#Function for adding a friend in social leaderboard
def socialAdd(request, people, social, notifications, push_notifications):
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

    posnots = notifications.find({'email': friendEmail}, {'_id': False})
    for nott in posnots:
        if nott['description'] == 'Social Add' and nott['senderEmail'] == userEmail and nott['read'] == False:
            response = jsonify([{'Success': False, 'Error': "Request already sent"
            }])
            response.status_code = 301
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
    send_notification(new_notification['email'], notString, 'Friend Request', push_notifications)

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

    updatedSList = senderFriends + [accepterEmail]
    updatedAList = accepterFriends + [senderEmail]

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
    send_notification(new_notification['email'], notString, 'Friend Request Accepted!', push_notifications)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

def get_completed_task_number_graph(email, social, people, goals):
    email = str.lower(email)
    socialObject = social.find_one({'email': email}, {'_id': False})
    child = people.find_one({'email': email}, {'_id': False})
    responseDict = {}
    for i in range(31):
        responseDict[i] = 0
    completedList = socialObject['tasksCompleted']
    quicksort_time(completedList)
    timeD = 0
    index = len(completedList)-1
    now = datetime.datetime.now()
    gridMax = 0
    while timeD <= 31:
        tdeltamin = datetime.timedelta(days = timeD)
        tdeltamax = datetime.timedelta(days = timeD + 1)
        tempgridMax = 0
        while index >= 0 and (now - completedList[index]) >= tdeltamin and (now - completedList[index]) <= tdeltamax:
            index -= 1
            responseDict[timeD] += 1
            tempgridMax += 1
        if tempgridMax > gridMax:
            gridMax = tempgridMax
        timeD += 1

    allGoals = goals.find({'email': email}, {'_id': False})
    maxVal = -1000000
    current = None
    for poss in allGoals:
        if not poss['redeemed'] and poss['approved']==1:
            if poss['value'] > maxVal:
                current = poss
                maxVal = poss['value']
    if current == None:
        retnum = 1
    else:
        retnum = child['balance']/float(maxVal)
    if retnum > 1:
        retnum = 1
    if len(str(float(100*float(retnum)))) > 3 and str(float(100*float(retnum)))[3] == '.':
        responseDict[timeD] = str(100*float(retnum))[:3]
    else:
        responseDict[timeD] = str(100*float(retnum))[:4]
    responseDict[timeD +1] = gridMax
    print(child['firstName'])
    print(responseDict)
    response = jsonify([responseDict
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
    friendsList = user['friends']
    responseDict = {}
    now = datetime.datetime.now()
    #Find the list first, then count the number of tasks completed/goals completed in the past week/month
    for friendEmail in friendsList:
        friend = {}
        statsObj = social.find_one({'email': friendEmail}, {'_id': False})
        person = people.find_one({'email': friendEmail}, {'_id': False})
        if person == None:
            continue
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
            run = 0
            current = completionDeadlineList[index]
            while ((now - current <= datetime.timedelta(days=7))):
                if now > current:
                    run += 1
                tasksCompletedDeadline +=1
                index -=1
                if index == -1:
                    break
                current = completionDeadlineList[index]
        totalTasksAssigned = get_total_tasks_week(tasks, friendEmail, now)
        if totalTasksAssigned == 0:
            taskCompleteRate = 1
        else:
            #Send rate as float
            totalTasksAssigned = totalTasksAssigned + run
            taskCompleteRate = float(tasksCompletedDeadline/totalTasksAssigned)
        if len(str(float(taskCompleteRate*100))) > 3:
            if str(float(taskCompleteRate*100))[3] == '.':
                friend['taskCompletionRateWeek'] = str(taskCompleteRate*100)[:3]
            else:
                friend['taskCompletionRateWeek'] = str(taskCompleteRate*100)[:4]
        else:
            friend['taskCompletionRateWeek'] = str(taskCompleteRate*100)
        if index >=0:
            while ((now - current <= datetime.timedelta(days=30))):
                tasksCompletedDeadline +=1
                index -=1
                if index == -1:
                    break
                current = completionDeadlineList[index]
        totalTasksAssigned = get_total_tasks_month(tasks,friendEmail, now)
        if totalTasksAssigned == 0:
            taskCompleteRate = 1
        else:
            totalTasksAssigned = totalTasksAssigned + run
            taskCompleteRate = float(tasksCompletedDeadline/totalTasksAssigned)
        if len(str(float(taskCompleteRate*100))) > 3:
            if str(float(taskCompleteRate*100))[3] == '.':
                friend['taskCompletionRateMonth'] = str(taskCompleteRate*100)[:3]
            else:
                friend['taskCompletionRateMonth'] = str(taskCompleteRate*100)[:4]
        else:
            friend['taskCompletionRateMonth'] = str(taskCompleteRate*100)
        friend['taskCompletionRateWeek'] = friend['taskCompletionRateMonth']
        friend['email'] = friendEmail
        friend['firstName'] = person['firstName']
        friend['lastName'] = person['lastName']
        if 'avatarColor' not in person:
            friend['avatarColor'] = '#000000'
        else:
            friend['avatarColor'] = person['avatarColor']
        responseDict[friendEmail] = friend
    response = jsonify(responseDict)
    response.status_code=200
    return response

def remFriend(request, people):
    request_json = request.get_json()
    emailOne = request_json['payLoad']['email']
    emailTwo = request_json['payLoad']['remFriend']
    emailOne = fixEmail(emailOne)
    emailTwo = fixEmail(emailTwo)
    personOne = people.find_one({'email': emailOne}, {'_id': False})
    personTwo = people.find_one({'email': emailTwo}, {'_id': False})
    friendListOne = personOne['friends']
    friendListTwo = personTwo['friends']
    if emailOne == emailTwo:
        response = jsonify([{'Error': 'You cannot remove yourself. That would be no fun!'
        }])
        response.status_code = 301
        return response
    if emailOne in friendListTwo and emailTwo in friendListOne:
        friendListOne.remove(emailTwo)
        friendListTwo.remove(emailOne)
    people.update_one({'email': emailOne}, {"$set":{'friends': friendListOne}},upsert = False)
    people.update_one({'email': emailTwo}, {"$set":{'friends': friendListTwo}},upsert = False)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

#Helper function to get the total number of tasks in a week
def get_total_tasks_week(tasks, friendEmail, now):
    count = 0
    all = tasks.find({'childEmail':str.lower(friendEmail)},{'_id': False})
    for task in all:
        if ((now - task['taskDeadline'] <= datetime.timedelta(days=7)) and now > task['taskDeadline']):
            count += 1
    return count

#Helper function to get the total number of tasks in a month
def get_total_tasks_month(tasks, friendEmail, now):
    count = 0
    all = tasks.find({'childEmail':str.lower(friendEmail)},{'_id': False})
    for task in all:
        if ((now - task['taskDeadline'] <= datetime.timedelta(days=30)) and now > task['taskDeadline']):
            count += 1
    return count
