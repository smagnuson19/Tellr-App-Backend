import jwt
import bcrypt
import random
from handleEmail import *
from flask import Flask, request, jsonify
import json
import datetime
from push import *
SECRET = "secret"

#Function for secure login and token generation
def authenticateUser(request, credentials, push_notifications):
    request_json = request.get_json()
    email = fixEmail(request_json['payLoad']['email'])
    pw = request_json['payLoad']['password']
    user = credentials.find_one({'email': email}, {'_id': False})
    print(request_json)
    #If we did get a user, raise an error
    if user == None:
        response = jsonify([{
        'Success': False,
        'Error' : "Incorrect username and password combo",
        }])
        response.status_code = 401
        return response

    #Otherwise make a token
    else:
        date = datetime.datetime.now()
        hash = user['password']
        if bcrypt.checkpw(pw.encode('utf-8'), hash):
            tokendict = {
                'sub': email,
                'iad': datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
            }
            # Generate token with date and encode it with secret
            token = jwt.encode(tokendict, SECRET, algorithm='HS256')
            testObj = push_notifications.find_one({'email': email})
            if testObj != None:
                push_notifications.update_one({'email': email}, {"$set":{'loggedIn': True}},upsert = False)
            response = jsonify([{
            'Success': True,
            'Token': token.decode('utf-8')
            }])
            response.status_code = 200
        #If wrong password, raise error
        else:
            response = jsonify([{
            'Success': False,
            'Error' : "Incorrect password",
            }])
            response.status_code = 401

    return response


def authLogout(request, push_notifications):
    request_json = request.get_json()
    push_notifications.update_one({'email': fixEmail(request_json['payLoad']['email'])}, {"$set":{'loggedIn': False}},upsert = False)
#Function for securely adding user login credentials during account creation
def authAddUser(request, people, credentials, social, push_notifications):
    if request.method == 'POST':
        request_json = request.get_json()
        #Check to see whether user is already in databse; if so, return empty json with 201 status
        if not people.find_one({'email':str.lower(request_json['payLoad']['email'])},{'_id': False}) == None:
            response = jsonify([{
            'Success': False,
            'Error' : 'Email already in use',
            }])
            response.status_code = 401
            response.detail = "Person exsits"
            return response

        #If not in databse, add to user and credentials database and return a 200 status code
        else:
            #Add a new person to the people database
            new_person = {
                'firstName': request_json['payLoad']['firstName'],
                'lastName': request_json['payLoad']['lastName'],
                'email': str.lower(request_json['payLoad']['email']),
                'familyName': str.lower(request_json['payLoad']['familyName']),
                'accountType': request_json['payLoad']['accountType'],
                'balance': 0.0,
                'notCounter': 0,
                'friends': [str.lower(request_json['payLoad']['email'])],
                'earnings': [(0, datetime.datetime.now(), 'BEGIN')],
                'avatarColor': request_json['payLoad']['avatarColor'],
                'color': 0
            }

            #Store password as a hash within credentials database
            password = request_json['payLoad']['password']
            hash = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            creds = {
                'email': str.lower(request_json['payLoad']['email']),
                'password': hash
            }

            date = datetime.datetime.now()
            tokendict = {
                'sub': str.lower(request_json['payLoad']['email']),
                'iad': datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
            }
            #Create a social entry to competitive stats purposes in social database
            socialEntry = {
                'email': str.lower(request_json['payLoad']['email']),
                'tasksCompleted': [],
                'goalsCompleted': [],
                'completionRate': []
            }


            push_entry = {
                'email': str.lower(request_json['payLoad']['email']),
                'pushID': request_json['payLoad']['oneSignalID'],
                'loggedIn': True
            }

            if not red[0]:
                retrivedError = (str(red[1])[5:-5])
                response = jsonify([{
                    'Success': False,
                    'Error': retrivedError
                }])
                response.status_code = 402
                return response

            people.insert_one(new_person)
            credentials.insert_one(creds)
            result3= social.insert_one(socialEntry)
            push_notifications.insert_one(push_entry)
            #Encode a token and send it
            token = jwt.encode(tokendict, SECRET, algorithm='HS256')
            response = jsonify([{
            'Success': True,
            'Token': token.decode('utf-8')
            }])

            response.status_code = 200
            return response

#Function to securely change password and send back a valid token
def authChangePassword(request, credentials):
    request_json = request.get_json()
    email = (verifyToken(request))[0]
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

#Function to allow users to change password using temporary password sent over email
def forgotPassword(request, credentials, mail, app):
    newPW = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16))
    request_json = request.get_json()
    email = request_json['payLoad']['email']
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

#Main wrapper function that verifies tokens at each endpoint
def verifyToken(request):
    untoken = str(request.headers.get('Authorization'))
    request_json = request.get_json()

    token = str.encode(untoken)
    try:
        decoded = jwt.decode(token, SECRET, algorithm='HS256')
    except:
        return("Invalid Token", False)

    now =datetime.datetime.now()
    if (now - datetime.datetime.strptime(decoded['iad'], "%Y-%m-%d %H:%M:%S")) > datetime.timedelta(days=180):
        return("Expired Token", False)

    else:
        return (decoded['sub'], True)
