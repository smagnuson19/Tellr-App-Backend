from flask import Flask, request, jsonify
from handleEmail import *
from flask_mail import Mail, Message

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
