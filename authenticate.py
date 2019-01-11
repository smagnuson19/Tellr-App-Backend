import jwt
import bcrypt
from handleEmail import *
from datetime import datetime
SECRET = "secret"

def authenticateUser(request, credentials):
    request_json = request.get_json()
    email = fixEmail(request_json['payLoad']['email'])
    pw = request_json['payLoad']['password']
    user = credentials.find_one({'email': email}, {'_id': False})
    hash = password['hash']
    if user == None:
        response = jsonify([{
        'Success': False,
        }])
        response.status_code = 201
        return response
    else:
        date = datetime.datetime.now()
        if bcrypt.checkpw(pw.encode('utf-8'), hash):
            tokendict = {
                'sub': email,
                'iad': datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
            }
            token = jwt.encode(tokendict, SECRET, algorithm='HS256')
            response = jsonify([{
            'Success': True,
            'Token': token
            }])
        else:
            response = jsonify([{
            'Success': False,
            }])
        response.status_code = 200
    return response

def authAddUser(request, people, credentials):
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

            token = jwt.encode(tokendict, SECRET, algorithm='HS256')
            response = jsonify([{'Success': True, 'Token': token
            }])
            response.status_code = 200
            return response

def verifyToken(request):
    request_json = request.get_json()
    token = request_json['payLoad']['token']
    try:
        decoded = jwt.decode(token, SECRET, algorithm='HS256')
    except:
        return("Invalid Token")

    now =datetime.datetime.now()
    if (now - datetime.datetime.strptime(decoded['iad'], "%Y-%m-%d %H:%M:%S")) > datetime.timedelta(hours=3):
        return("Expired Token")

    else:
        return decoded['sub']
