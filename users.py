from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message
from push import *
import datetime

#Adding a user to the database
def add_user(request, people, credentials, social, push_notifications):
    if request.method == 'POST':
        request_json = request.get_json()
        #Check to see whether user is already in databse; if so, return empty json with 201 status
        if not people.find_one({'email':str.lower(request_json['payLoad']['email'])},{'_id': False}) == None:
            response = jsonify([{
            'Success': False,
            'Error': 'Email already exists'
            }])
            response.status_code = 401
            return response

        #If not in databse, add to user and credentials database and return a 200 status code
        else:
            new_person = {
                'firstName': request_json['payLoad']['firstName'],
                'lastName': request_json['payLoad']['lastName'],
                'email': str.lower(request_json['payLoad']['email']),
                'password': request_json['payLoad']['password'],
                'familyName': str.lower(request_json['payLoad']['familyName']),
                'accountType': request_json['payLoad']['accountType'],
                'balance': 0.0,
                'notCounter': 0,
                'friends': [str.lower(request_json['payLoad']['email'])]
            }
            result1 = people.insert_one(new_person)
            creds = {
                'email': str.lower(request_json['payLoad']['email']),
                'password': request_json['payLoad']['password']
            }
            result2= credentials.insert_one(creds)

            socialEntry = {
                'email': str.lower(request_json['payLoad']['email']),
                'tasksCompleted': [],
                'goalsCompleted': [],
                'completionRate': []
            }


            result3= social.insert_one(socialEntry)
            response = jsonify([{'Success': True,
            }])
            response.status_code = 200
            return response

#Function that returns dictionary of all children of parent with given email
def findChildren(email, people):
    #First find the parent
    user = people.find_one({'email': str.lower(email)}, {'_id': False})
    #If invalid email, return empty json with 201 status
    if user == None:
        response = jsonify([{'Success': False,
        'Error': 'No children found'
        }])
        response.status_code=401
    #Else, find all children with the same family name
    else:
        childrenList = people.find({'familyName':str.lower(user['familyName'])},{'_id': False})
        dictresponse = {}
        i = 0
        for child in childrenList:
            if child['accountType']=='Child':
                dictresponse[i]=child
                i = i+1
        print(dictresponse)
        response = jsonify(dictresponse)
        response.status_code = 200
    return response

def getUserHistory(email, people):
    child = people.find_one({'email': str.lower(email)}, {'_id': False})
    earnings_history = child['earnings']
    dictresponse = {}
    for i in range(len(earnings_history)):
        dictresponse[i] = list(earnings_history[i])
        dictresponse[i][1] = str(dictresponse[i][1])[:10]
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

def getUserHistoryWeek(email, people):
    child = people.find_one({'email': str.lower(email)}, {'_id': False})
    earnings_history = child['earnings']
    now = datetime.datetime.now()
    dictresponse = {}
    for i in range(len(earnings_history)):
        j = i
        i = len(earnings_history) - i -1
        if (now - earnings_history[i][1]) < datetime.timedelta(days = 7):
            dictresponse[j] = list(earnings_history[i])
            dictresponse[j][1] = str(dictresponse[j][1])[:10]
        else:
            break
    response = jsonify(dictresponse)
    response.status_code = 200
    return dictresponse

def getUserHistoryMonth(email, people):
    child = people.find_one({'email': str.lower(email)}, {'_id': False})
    earnings_history = child['earnings']
    now = datetime.datetime.now()
    dictresponse = {}
    for i in range(len(earnings_history)):
        j=i
        i = len(earnings_history)  - i -1
        if (now - earnings_history[i][1]) < datetime.timedelta(days = 31):
            dictresponse[j] = list(earnings_history[i])
            dictresponse[j][1] = str(dictresponse[j][1])[:10]
        else:
            break
    response = jsonify(dictresponse)
    response.status_code = 200
    return dictresponse

def getUserHistoryYear(email, people):
    child = people.find_one({'email': str.lower(email)}, {'_id': False})
    earnings_history = child['earnings']
    now = datetime.datetime.now()
    dictresponse = {}
    for i in range(len(earnings_history)):
        j=i
        i = len(earnings_history)  - i -1
        if (now - earnings_history[i][1]) < datetime.timedelta(days = 365):
            dictresponse[j] = list(earnings_history[i])
            dictresponse[j][1] = str(dictresponse[j][1])[:10]
        else:
            break
    response = jsonify(dictresponse)
    response.status_code = 200
    return dictresponse

def getAnalyticsAll(email, people):
    d1 = getAnalyticsWeek(email, people)
    d2 = getAnalyticsMonth(email, people)
    d3 = getAnalyticsYear(email, people)
    d1['balanceGraph'] = getUserHistoryWeek(email, people)
    d2['balanceGraph'] = getUserHistoryMonth(email, people)
    d3['balanceGraph'] = getUserHistoryYear(email, people)
    dictresponse = {}
    dictresponse[0] = d1
    dictresponse[1] = d2
    dictresponse[2] = d3
    response = jsonify(dictresponse)
    response.status_code = 200
    return response

def getAnalyticsWeek(email, people):
    child = people.find_one({'email': str.lower(email)}, {'_id': False})
    earnings_history = child['earnings']
    now = datetime.datetime.now()
    tasksCompleted = 0
    goalsRedeemed = 0
    moneyReeemed = 0
    task_earned = 0
    goal_used = 0
    redemptions = 0
    allowance = 0
    to_operate = ""
    numAllowances = 0
    pos = []
    neg = []
    first = True
    for i in range(len(earnings_history)):
        i = len(earnings_history) - i -1
        if to_operate == 'TASK':
            task_earned += currentBalance - earnings_history[i][0]
        elif to_operate == 'GOAL':
            goal_used +=  earnings_history[i][0] - currentBalance
        elif to_operate == 'RED':
            moneyReeemed += earnings_history[i][0] - currentBalance
        elif to_operate == 'UP':
            allowance += currentBalance - earnings_history[i][0]

        if (now - earnings_history[i][1]) < datetime.timedelta(days = 7):
            if earnings_history[i][2] == 'TASK':
                tasksCompleted += 1
                to_operate = 'TASK'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
            if earnings_history[i][2] == 'GOAL':
                goalsRedeemed += 1
                to_operate = 'GOAL'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]

            if earnings_history[i][2] == 'RED':
                redemptions += 1
                to_operate = 'RED'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]

            if earnings_history[i][2] == 'UP':
                numAllowances += 1
                to_operate = 'UP'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
        else:
            break
    dictresponse = {}
    dictresponse['tasksCompleted'] = tasksCompleted
    dictresponse['goalsRedeemed'] = goalsRedeemed
    dictresponse['redemptions'] = redemptions
    dictresponse['moneyReeemed'] = moneyReeemed
    dictresponse['task_earned'] = task_earned
    dictresponse['goal_used'] = goal_used
    dictresponse['redemptions'] = redemptions
    if tasksCompleted == 0:
        dictresponse['avgTask'] = 0
    else:
        dictresponse['avgTask'] = float(task_earned/tasksCompleted)
    if goalsRedeemed == 0:
        dictresponse['avgGoal'] = 0
    else:
        dictresponse['avgGoal'] = float(goal_used/goalsRedeemed)
    dictresponse['net'] = task_earned - moneyReeemed - goal_used + allowance
    dictresponse['rate'] = dictresponse['net']
    dictresponse['allowance'] = allowance
    dictresponse['numAllowances'] = numAllowances

    pind = 0
    nind = 0
    retPos = []
    retNeg = []
    pmax = len(pos)-1
    nmax = len(neg)-1

    for i in range(7):
        i = 5.5-i
        tempSumPos = 0
        tempSumNeg = 0
        while pind <= pmax and (now-pos[pind][1]) > datetime.timedelta(days = i):
            tempSumPos = tempSumPos + pos[pind][0]
            pind += 1
        retPos.insert(0, tempSumPos)
        while nind <= nmax and (now - neg[nind][1] > datetime.timedelta(days = i)):
            tempSumNeg = tempSumNeg + neg[nind][0]
            nind += 1
        retNeg.insert(0, tempSumNeg)

    dictresponse['retPos'] = retPos
    dictresponse['retNeg'] = retNeg
    response = jsonify(dictresponse)
    response.status_code = 200
    return dictresponse

def getAnalyticsMonth(email, people):
    child = people.find_one({'email': str.lower(email)}, {'_id': False})
    earnings_history = child['earnings']
    now = datetime.datetime.now()
    tasksCompleted = 0
    goalsRedeemed = 0
    moneyReeemed = 0
    task_earned = 0
    goal_used = 0
    redemptions = 0
    allowance = 0
    to_operate = ""
    numAllowances = 0
    pos = []
    neg = []
    first = True

    for i in range(len(earnings_history)):
        i = len(earnings_history) - i -1
        if to_operate == 'TASK':
            task_earned += currentBalance - earnings_history[i][0]
        elif to_operate == 'GOAL':
            goal_used +=  earnings_history[i][0] - currentBalance
        elif to_operate == 'RED':
            moneyReeemed += earnings_history[i][0] - currentBalance
        elif to_operate == 'UP':
            allowance += currentBalance - earnings_history[i][0]

        if (now - earnings_history[i][1]) < datetime.timedelta(days = 31):
            if earnings_history[i][2] == 'TASK':
                tasksCompleted += 1
                to_operate = 'TASK'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
            if earnings_history[i][2] == 'GOAL':
                goalsRedeemed += 1
                to_operate = 'GOAL'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
            if earnings_history[i][2] == 'RED':
                redemptions += 1
                to_operate = 'RED'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
            if earnings_history[i][2] == 'UP':
                numAllowances += 1
                to_operate = 'UP'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
        else:
            break
    dictresponse = {}
    dictresponse['tasksCompleted'] = tasksCompleted
    dictresponse['goalsRedeemed'] = goalsRedeemed
    dictresponse['redemptions'] = redemptions
    dictresponse['moneyReeemed'] = moneyReeemed
    dictresponse['task_earned'] = task_earned
    dictresponse['goal_used'] = goal_used
    dictresponse['redemptions'] = redemptions
    if tasksCompleted == 0:
        dictresponse['avgTask'] = 0
    else:
        dictresponse['avgTask'] = float(task_earned/tasksCompleted)
    if goalsRedeemed == 0:
        dictresponse['avgGoal'] = 0
    else:
        dictresponse['avgGoal'] = float(goal_used/goalsRedeemed)
    dictresponse['net'] = task_earned - moneyReeemed - goal_used +allowance
    dictresponse['rate'] = float(dictresponse['net']*7/31)
    dictresponse['allowance'] = allowance
    dictresponse['numAllowances'] = numAllowances

    pind = 0
    nind = 0
    retPos = []
    retNeg = []
    for i in range(8):
        i = 7-i
        days = i*3.8-.5
        tempSumPos = 0
        tempSumNeg = 0
        pmax = len(pos)-1
        nmax = len(neg)-1

        while pind <= pmax and (now-pos[pind][1]) > datetime.timedelta(days = days):
            tempSumPos = tempSumPos + pos[pind][0]
            pind += 1
        retPos.insert(0, tempSumPos)
        while nind <= nmax and (now - neg[nind][1] > datetime.timedelta(days = days)):
            tempSumNeg = tempSumNeg + neg[nind][0]
            nind += 1

        retNeg.insert(0, tempSumNeg)
    dictresponse['retPos'] = retPos
    dictresponse['retNeg'] = retNeg

    response = jsonify(dictresponse)
    response.status_code = 200
    return dictresponse

def getAnalyticsYear(email, people):
    child = people.find_one({'email': str.lower(email)}, {'_id': False})
    earnings_history = child['earnings']
    now = datetime.datetime.now()
    tasksCompleted = 0
    goalsRedeemed = 0
    moneyReeemed = 0
    task_earned = 0
    goal_used = 0
    redemptions = 0
    allowance = 0
    to_operate = ""
    numAllowances = 0
    pos = []
    neg = []
    first = True

    for i in range(len(earnings_history)):
        i = len(earnings_history) - i - 1
        if to_operate == 'TASK':
            task_earned += currentBalance - earnings_history[i][0]
        elif to_operate == 'GOAL':
            goal_used +=  earnings_history[i][0] - currentBalance
        elif to_operate == 'RED':
            moneyReeemed += earnings_history[i][0] - currentBalance
        elif to_operate == 'UP':
            allowance += currentBalance - earnings_history[i][0]

        if (now - earnings_history[i][1]) < datetime.timedelta(days = 365):
            if earnings_history[i][2] == 'TASK':
                tasksCompleted += 1
                to_operate = 'TASK'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
            if earnings_history[i][2] == 'GOAL':
                goalsRedeemed += 1
                to_operate = 'GOAL'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
            if earnings_history[i][2] == 'RED':
                redemptions += 1
                to_operate = 'RED'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
            if earnings_history[i][2] == 'UP':
                numAllowances += 1
                to_operate = 'UP'
                if not first:
                    if (currentBalance - earnings_history[i][0]) > 0:
                        pos.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                    else:
                        neg.insert(0, (currentBalance - earnings_history[i][0], earnings_history[i][1]))
                first = False
                currentBalance = earnings_history[i][0]
        else:
            break
    dictresponse = {}
    dictresponse['tasksCompleted'] = tasksCompleted
    dictresponse['goalsRedeemed'] = goalsRedeemed
    dictresponse['redemptions'] = redemptions
    dictresponse['moneyReeemed'] = moneyReeemed
    dictresponse['task_earned'] = task_earned
    dictresponse['goal_used'] = goal_used
    dictresponse['redemptions'] = redemptions
    if tasksCompleted == 0:
        dictresponse['avgTask'] = 0
    else:
        dictresponse['avgTask'] = float(task_earned/tasksCompleted)
    if goalsRedeemed == 0:
        dictresponse['avgGoal'] = 0
    else:
        dictresponse['avgGoal'] = float(goal_used/goalsRedeemed)
    dictresponse['net'] = task_earned - moneyReeemed - goal_used +allowance
    dictresponse['rate'] = float(dictresponse['net']*7/365)
    dictresponse['allowance'] = allowance
    dictresponse['numAllowances'] = numAllowances

    pind = 0
    nind = 0
    retPos = []
    retNeg = []
    for i in range(6):
        i = 5-i
        days = i*61-1
        tempSumPos = 0
        tempSumNeg = 0
        pmax = len(pos)-1
        nmax = len(neg)-1
        while pind <= pmax and (now-pos[pind][1]) > datetime.timedelta(days = days):
            tempSumPos = tempSumPos + pos[pind][0]
            pind += 1
        retPos.insert(0, tempSumPos)
        while nind <= nmax and (now - neg[nind][1]) > datetime.timedelta(days = days):
            tempSumNeg = tempSumNeg + neg[nind][0]
            nind += 1
        retNeg.insert(0, tempSumNeg)
    dictresponse['retPos'] = retPos
    dictresponse['retNeg'] = retNeg

    response = jsonify(dictresponse)
    response.status_code = 200
    return dictresponse

#Function that updates balance
def upBalance(request,people,notifications, mail, app):
    request_json = request.get_json()
    user = people.find_one({'email': fixEmail(request_json['payLoad']['email'])}, {'_id': False})
    #If email given isn't in the database, make an empty json and return status code 201
    if user == None:
        response = jsonify([{'Success': False,
        'Error': 'User not found'
        }])
        response.status_code=401
    #If email is found, update the balance and return 200 status code
    else:
        lastbal = user['balance']
        people.update_one({'email': fixEmail(user['email'])}, {"$set":{'balance': lastbal + float(request_json['payLoad']['increment'])}},upsert = False)
        earnings_history = user['earnings']
        earnings_history.append((lastbal + float(request_json['payLoad']['increment']), datetime.datetime.now(), 'UP'))
        people.update_one({'email': user['email']},{"$set":{'earnings': earnings_history}},upsert = False)
        sender = people.find_one({'email': fixEmail(request_json['payLoad']['senderEmail'])}, {'_id': False})
        new_notification = {
            'email': user['email'],
            'accountType': 'Child',
            'notificationType': 'balanceChange',
            'notificationName': float(request_json['payLoad']['increment']),
            'description': lastbal + float(request_json['payLoad']['increment']),
            'senderName': sender['firstName'],
            'senderEmail': sender['email'],
            'priority': user['notCounter'],
            'value': float(request_json['payLoad']['increment']),
            'read': False
        }
        notifications.insert_one(new_notification)
        current_priority = user['notCounter']
        people.update_one({'email': user['email']}, {"$set":{'notCounter': current_priority+1}},upsert = False)
        # for char in user['email']:
        #     if char == "@":
        #         mstring = "Exciting news " + user['firstName'] + ", your balance on tellr has changed... Make sure to visit our ~app~ to find out just how close you are to your next goal!"
        #         with app.app_context():
        #             msg = Message("Dun dun dunnnnnn",
        #                               sender="teller.notifications@gmail.com",
        #                               recipients=[user['email']])
        #             msg.body = mstring
        #             mail.send(msg)
        response = jsonify([{
        }])
        response.status_code=200

    return response

#Function for deleting all users of a given family name
def delAllUser(request,people, credentials):
    person = people.find_one({'email': (request.get_json()['payLoad']['email'])}, {'_id': False})
    if person.accountType == 'Parent':
        for member in people.find({'familyName': person['familyName']}):
            credentials.delete_one({ "email": member['email'] })
            people.delete_one({ "email": member['email'] })
    credentials.delete_one({ "email": fixEmail(request.get_json()['payLoad']['email']) })
    people.delete_one({"email": fixEmail(request.get_json()['payLoad']['email'])})
    response = jsonify([{
    }])
    response.status_code=200

    return response

#Function to delete one user
def delOne(request, people, credentials):
    credentials.delete_one({ "email": fixEmail(request.get_json()['payLoad']['email']) })
    people.delete_one({"email": fixEmail(request.get_json()['payLoad']['email'])})
    response = jsonify([{
    }])
    response.status_code=200

    return response
