from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message

#Adding a user to the database
def add_user(request, people, credentials):
    if request.method == 'POST':
        request_json = request.get_json()
        #Check to see whether user is already in databse; if so, return empty json with 201 status
        if not people.find_one({'email':str.lower(request_json['payLoad']['email'])},{'_id': False}) == None:
            response = jsonify([{'Success': False,
            }])
            response.status_code = 201
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
                'notCounter': 0
            }
            result1 = people.insert_one(new_person)
            creds = {
                'email': str.lower(request_json['payLoad']['email']),
                'password': request_json['payLoad']['password']
            }
            result2= credentials.insert_one(creds)
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
        response = jsonify([{
        }])
        response.status_code=201
    #Else, find all children with the same family name
    else:
        childrenList = people.find({'familyName':str.lower(user['familyName'])},{'_id': False})
        dictresponse = {}
        i = 0
        for child in childrenList:
            print(child)
            if child['accountType']=='Child':
                dictresponse[i]=child
                i = i+1
        print(dictresponse)
        response = jsonify(dictresponse)
        response.status_code = 200
    return response

#Function that updates balance
def upBalance(request,people,notifications, mail, app):
    request_json = request.get_json()
    user = people.find_one({'email': fixEmail(request_json['payLoad']['email'])}, {'_id': False})
    #If email given isn't in the database, make an empty json and return status code 201
    if user == None:
        response = jsonify([{
        }])
        response.status_code=201
    #If email is found, update the balance and return 200 status code
    else:
        lastbal = user['balance']
        people.update_one({'email': fixEmail(user['email'])}, {"$set":{'balance': lastbal + float(request_json['payLoad']['increment'])}},upsert = False)
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
        for char in user['email']:
            if char == "@":
                mstring = "Exciting news " + user['firstName'] + ", your balance on tellr has changed... Make sure to visit our ~app~ to find out just how close you are to your next goal!"
                with app.app_context():
                    msg = Message("Dun dun dunnnnnn",
                                      sender="teller.notifications@gmail.com",
                                      recipients=[user['email']])
                    msg.body = mstring
                    mail.send(msg)
        response = jsonify([{
        }])
        response.status_code=200

    return response
