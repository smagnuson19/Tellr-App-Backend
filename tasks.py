from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message
import datetime
from push import *

#Function to get all tasks for a given family name
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

#Function to allow parents to post tasks for their kids
def postTask(request,tasks, people, notifications, mail, app, push_notifications):
    request_json = request.get_json()
    if request_json['payLoad']['childEmail'] == '':
        response = jsonify([{'Success': False,
        'Error': 'No children selected'
        }])
        response.status_code = 401
        return response
    send_notification(fixEmail(str.lower(request_json['payLoad']['senderEmail'])), 'It works!', 'heading', push_notifications)
    child = people.find_one({'email':fixEmail(request_json['payLoad']['childEmail'])},{'_id': False})
    stringName = child['firstName']+ ' '+ child['lastName']

    #Store deadline as a datetime object (convert from string)
    date_time_str = request_json['payLoad']['taskDeadline']
    print(date_time_str)
    datelist = date_time_str.split()
    now = datetime.datetime.now()
    print(datelist)
    realstr = datelist[0][:3] + " "+ datelist[1][:-3] + " " + str(now.year) +  " "  + datelist[2]
    date_time_obj = datetime.datetime.strptime(realstr, '%b %d %Y %I:%M%p')
    now = datetime.datetime.now()

    if (date_time_obj - now) < datetime.timedelta(hours=0):
        response = jsonify([{'Success': False, 'Error': 'Task Deadline has already passed!'
        }])
        response.status_code = 401
        return response

    #Create new task entry and store in tasks database
    new_task = {
        'taskName': request_json['payLoad']['taskName'],
        'reward': float(request_json['payLoad']['reward']),
        'taskDeadline': date_time_obj,
        'taskDescription': request_json['payLoad']['taskDescription'],
        'childEmail': fixEmail(request_json['payLoad']['childEmail']),
        'senderEmail': fixEmail(str.lower(request_json['payLoad']['senderEmail'])),
        'childName': stringName,
        'complete': False,
        'verified': False,
        'dateCompleted': None,
        'familyName': child['familyName'],
        'timeCompleted': None,
        'alert': False
    }

    result1 = tasks.insert_one(new_task)
    parent = people.find_one({'email': new_task['senderEmail']},{'_id': False})
    sName = parent['firstName']+ ' '+ parent['lastName']

    now =datetime.datetime.now()
    if (new_task['taskDeadline']-now) < datetime.timedelta(hours=24):
        display = True
    else:
        display = False

    #Notify child that they have a new task
    new_notification = {
        'email': child['email'],
        'accountType': 'Child',
        'notificationType': 'newTask',
        'notificationName': new_task['taskName'],
        'description': new_task['taskDescription'],
        'senderName': parent['firstName'],
        'senderEmail': parent['email'],
        'priority': child['notCounter'],
        'value': new_task['reward'],
        'read': False,
        'deadline': datetime.datetime.strftime(new_task['taskDeadline'], '%b %d %Y %I:%M%p'),
        'displayRed': display
    }
    notifications.insert_one(new_notification)
    current_priority = child['notCounter']
    people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
    # mstring = "You've got money! (almost...) Your parents have posted a new task: " + new_task['taskName'] + "! Make sure to check out your tellrApp for details and complete this task before the deadline passes!"
    # for char in child['email']:
    #     if char == "@":
    #         with app.app_context():
    #             msg = Message("You've Got a New Money Opportunity!",
    #                               sender="teller.notifications@gmail.com",
    #                               recipients=[child['email']])
    #             msg.body = mstring
    #             mail.send(msg)
    notString = 'A new task ' + new_task['taskName'] + ' has been created!'

    # Waiting for OneSignal account to test
    # send_notification(client, child['email'], notString, 'New Task Created!', push_notifications)

    response = jsonify([{
    }])
    response.status_code = 200
    return response

#Get tasks list for all children
def getTasksChild(email, tasks):
    tasksList = tasks.find({'childEmail':str.lower(email)},{'_id': False})
    dictresponse = {}
    i = 0
    for task in tasksList:
        task['taskDeadline'] = str(task['taskDeadline'])
        dictresponse[i]=task
        i = i+1
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

#Handle when children complete tasks
def completeTask(request, tasks, notifications, people, mail, app):
    request_json = request.get_json()
    child = people.find_one({'email':fixEmail(request_json['payLoad']['email'])})
    stringName = child['firstName']+ ' '+ child['lastName']
    tasksList = tasks.find({'childEmail':fixEmail(str.lower(request_json['payLoad']['email']))})
    now = datetime.datetime.now()
    for task in tasksList:
        if task['taskName'] == request_json['payLoad']['taskName']:
            actualT = task
            tasks.update_one({'_id': task['_id']}, {"$set":{'complete': True}},upsert = False)
            tasks.update_one({'_id': task['_id']}, {"$set":{'timeCompleted': now}},upsert = False)
            parent = people.find_one({'email':str.lower(task['senderEmail'])})
            new_notification = {
                'email': task['senderEmail'],
                'accountType': 'Parent',
                'notificationType': 'taskComplete',
                'notificationName': task['taskName'],
                'description': task['taskDescription'],
                'deadline':  datetime.datetime.strftime(task['taskDeadline'], '%b %d %Y %I:%M%p'),
                'senderName': stringName,
                'senderEmail': child['email'],
                'priority': parent['notCounter'],
                'value': task['reward'],
                'read': False
            }
            print(new_notification)
            print(task)
            notifications.insert_one(new_notification)
            current_priority = parent['notCounter']
            people.update_one({'email': parent['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
    #
    # mstring = "Your child has completed the task: " + actualT['taskName'] + ". Please visit tellrApp to see details and to verify!"
    # for char in task['senderEmail']:
    #     if char == "@":
    #         with app.app_context():
    #             msg = Message("Task Completed",
    #                               sender="teller.notifications@gmail.com",
    #                               recipients=[task['senderEmail']])
    #             msg.body = mstring
    #             mail.send(msg)

    response = jsonify([{
    }])
    response.status_code = 200
    return response

#Function to allow parents to verfiy tasks
def verifyTask(request, tasks, notifications, people, mail, app, social, push_notifications):
    request_json = request.get_json()
    child = people.find_one({'email':fixEmail(request_json['payLoad']['email'])})
    tasksList = tasks.find({'childEmail': fixEmail(request_json['payLoad']['email'])})
    if request_json['payLoad']['verify'] == True:
        for task in tasksList:
            if task['taskName'] == request_json['payLoad']['taskName']:
                actualT = task
                tasks.update_one({'_id': task['_id']}, {"$set":{'verified': True}},upsert = False)
                parent = people.find_one({'email':fixEmail(task['senderEmail'])})
                stringName = parent['firstName']+ ' '+ parent['lastName']
                #Notify children
                new_notification={
                    'email': child['email'],
                    'accountType': 'Child',
                    'notificationType': 'taskVerified',
                    'notificationName': task['taskName'],
                    'description': task['taskDescription'],
                    'senderName': parent['firstName'],
                    'senderEmail': parent['email'],
                    'priority': child['notCounter'],
                    'value': task['reward'],
                    'read': False
                }

                notifications.insert_one(new_notification)
                current_priority = child['notCounter']
                #update balance of children
                new_balance = child['balance'] + float(task['reward'])
                people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
                people.update_one({'email': child['email']}, {"$set":{'balance': new_balance}},upsert = False)

                earnings_history = child['earnings']
                earnings_history.append((new_balance, datetime.datetime.now(), 'TASK'))
                people.update_one({'email': child['email']},{"$set":{'earnings': earnings_history}},upsert = False)
                break
        #update social entries accordingly for tasks and task completion rate
        now = datetime.datetime.now()
        socialEntry = social.find_one({'email':fixEmail(request_json['payLoad']['email'])})
        newList = socialEntry['tasksCompleted']
        newList.append(actualT['timeCompleted'])
        social.update_one({'email': socialEntry['email']}, {"$set":{'tasksCompleted': newList}},upsert = False)
        nList = socialEntry['completionRate']
        deadline = actualT['taskDeadline']
        nList.append(deadline)
        social.update_one({'email': socialEntry['email']}, {"$set":{'completionRate': nList}},upsert = False)
        # mstring = "Awesome work " + child['firstName'] + ", your completion of the task: " + actualT['taskName'] + " has been verified. See your tellrApp for your updated balanc !"
        # print("test")
        # for char in child['email']:
        #     if char == "@":
        #         with app.app_context():
        #             msg = Message("Cha Ching!",
        #                               sender="teller.notifications@gmail.com",
        #                               recipients=[child['email']])
        #             msg.body = mstring
        #             mail.send(msg)

        # notString = 'Completion of your task ' + payLoad['taskName'] + ' has verified! Your balance has been updated.'

        # Waiting for OneSignal account to test
        # send_notification(client, child['email'], notString, 'Task Completion Verified!', push_notifications)

        response = jsonify([{
        }])
        response.status_code = 200
        return response
    else:
        #If parents deny the completion, notify children and re-publish the task
        for task in tasksList:
            if task['taskName'] == request_json['payLoad']['taskName']:
                tasks.update_one({'_id': task['_id']}, {"$set":{'complete': False}},upsert = False)
                tasks.update_one({'_id': task['_id']}, {"$set":{'timeCompleted': None}},upsert = False)
                parent = people.find_one({'email':fixEmail(task['senderEmail'])})
                now =datetime.datetime.now()
                if (task['taskDeadline']-now) < datetime.timedelta(hours=24):
                    display = True
                else:
                    display = False
                new_notification={
                    'email': child['email'],
                    'accountType': 'Child',
                    'notificationType': 'taskUnverified',
                    'notificationName': task['taskName'],
                    'description': task['taskDescription'],
                    'senderName': parent['firstName'],
                    'senderEmail': parent['email'],
                    'priority': child['notCounter'],
                    'deadline':  datetime.datetime.strftime(task['taskDeadline'], '%b %d %Y %I:%M%p'),
                    'value': task['reward'],
                    'read': False,
                    'displayRed': display
                }
                notifications.insert_one(new_notification)
                current_priority = child['notCounter']
                people.update_one({'email': child['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
                break

                notString = 'Completion of your task ' + payLoad['taskName'] + ' has been denied! Please click here to redo your task.'

                # Waiting for OneSignal account to test
                # send_notification(client, child['email'], notString, 'Task Completion Denied', push_notifications)
        response = jsonify([{
        }])
        response.status_code = 200
        return response

def getCompletedTasks(request, tasks):
    request_json = request.get_json()
    counter = 0
    returnList = []
    tasksList = tasks.find({'childEmail': fixEmail(request_json['payLoad']['email'])}, {'_id': False})

    for task in tasksList:
        if task['verified'] == True:
            returnList.append(task)

    quicksort_time(returnList)
    returnDict = {}
    for index in range(len(returnList)):
        returnDict[index] = returnList[index]

    response = jsonify([returnDict
        ])
    response.status_code = 200
    return response


def partition(the_list, p, r):
    i = p - 1              # i demarcates the end of the sublist containing values <= pivot.
    j = p                  # j demarcates end of sublist containing values > pivot.
    pivot = the_list[r]['taskDeadline']    # Pivot will store value of sublist's last item.
    while j < r:
        if the_list[j]['taskDeadline'] < pivot:
            j += 1         # Increment j.
        elif the_list[j]['taskDeadline'] >= pivot:
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
