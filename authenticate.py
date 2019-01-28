import jwt
import bcrypt
import random
from handleEmail import *
from flask import Flask, request, jsonify
import json
import datetime
SECRET = "secret"

def authenticateUser(request, credentials):
    request_json = request.get_json()
    email = fixEmail(request_json['payLoad']['email'])
    pw = request_json['payLoad']['password']
    user = credentials.find_one({'email': email}, {'_id': False})

    if user == None:
        response = jsonify([{
        'Success': False,
        'Error' : "Inccorect username and password combo",
        }])
        response.status_code = 401
        return response
    else:
        date = datetime.datetime.now()
        hash = user['password']
        if bcrypt.checkpw(pw.encode('utf-8'), hash):
            tokendict = {
                'sub': email,
                'iad': datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
            }
            token = jwt.encode(tokendict, SECRET, algorithm='HS256')
            response = jsonify([{
            'Success': True,
            'Token': token.decode('utf-8')
            }])
            response.status_code = 200
        else:
            response = jsonify([{
            'Success': False,
            'Error' : "Inccorect password",
            }])
            response.status_code = 401

    return response

def authAddUser(request, people, credentials, social):
    if request.method == 'POST':
        request_json = request.get_json()
        #Check to see whether user is already in databse; if so, return empty json with 201 status
        if not people.find_one({'email':str.lower(request_json['payLoad']['email'])},{'_id': False}) == None:
            response = jsonify([{'Success': False,
            }])
            response.status_code = 401
            response.detail = "Person exsits"
            return response

        #If not in databse, add to user and credentials database and return a 200 status code
        else:
            new_person = {
                'firstName': request_json['payLoad']['firstName'],
                'lastName': request_json['payLoad']['lastName'],
                'email': str.lower(request_json['payLoad']['email']),
                'familyName': str.lower(request_json['payLoad']['familyName']),
                'accountType': request_json['payLoad']['accountType'],
                'balance': 0.0,
                'notCounter': 0
            }
            people.insert_one(new_person)
            password = request_json['payLoad']['password']
            hash = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            creds = {
                'email': str.lower(request_json['payLoad']['email']),
                'password': hash
            }
            credentials.insert_one(creds)
            date = datetime.datetime.now()
            tokendict = {
                'sub': str.lower(request_json['payLoad']['email']),
                'iad': datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
            }

            socialEntry = {
                'email': str.lower(request_json['payLoad']['email']),
                'tasksCompleted': [],
                'goalsCompleted': [],
                'completionRate': []
            }
            result3= social.insert_one(socialEntry)

            token = jwt.encode(tokendict, SECRET, algorithm='HS256')
            response = {'Success': True, 'Token': token.decode('utf-8')
            }
            print(response)
            response= jsonify(response)
            response.status_code = 200
            return response

def authChangePassword(request, credentials):
    request_json = request.get_json()
    email = (verifyToken(request))
    if (not email =='Invalid Token') and (not email == 'Expired Token'):
        newpassword = request_json['payLoad']['newPassword']
        pw = request_json['payLoad']['password']
        user = credentials.find_one({'email': fixEmail(email)}, {'_id': False})
        hash = user['password']
        if bcrypt.checkpw(pw.encode('utf-8'), hash):
            newhash = bcrypt.hashpw(newpassword.encode('utf-8'),bcrypt.gensalt())
            credentials.update_one({'email': fixEmail(email)}, {"$set":{'password': newhash}},upsert = False)
            response = jsonify([{'Success': True}])
            response.status_code = 200
            return response
        else:
            response = jsonify([{'Success': False, 'Error' : "Inccorect password"
            }])
            response.status_code = 401
            return response
    else:
        response = jsonify([{'Success': False, 'Error' : "Invalid/Expired Token"
        }])
        response.status_code = 401
        return response

def forgotPassword(request, credentials, mail, app):
    newPW = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16))
    email = (verifyToken(request))
    if (not email =='Invalid Token') and (not email == 'Expired Token'):
        email = fixEmail(email)
        newhash = bcrypt.hashpw(newPW.encode('utf-8'),bcrypt.gensalt())
        credentials.update_one({'email': email}, {"$set":{'password': newhash}},upsert = False)
        mstring = "Your new Tellr password is: " + newPW
        for char in email:
            if char == "@":
                with app.app_context():
                    msg = Message("Your Tellr Password Reset Request",
                        sender="teller.notifications@gmail.com",
                        recipients=[email])
                    msg.body = mstring
                    mail.send(msg)
        response = jsonify([{'Success': True}])
        response.status_code = 200
        return response

    else:
        response = jsonify([{'Success': False, 'Error' : "Invalid/Expired Token"
        }])
        response.status_code = 401
        return response

def verifyToken(request):
    request_json = request.get_json()
    untoken = request_json['payLoad']['token']
    token = str.encode(untoken)
    try:
        decoded = jwt.decode(token, SECRET, algorithm='HS256')
    except:
        return("Invalid Token")

    now =datetime.datetime.now()
    if (now - datetime.datetime.strptime(decoded['iad'], "%Y-%m-%d %H:%M:%S")) > datetime.timedelta(days=3):
        return("Expired Token")

    else:
        return decoded['sub']
