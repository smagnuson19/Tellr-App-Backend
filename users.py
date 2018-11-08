from flask import Flask, request, jsonify

def add_user(request, people, credentials):
    if request.method == 'POST':
        request_json = request.get_json()
        # people.update_one({'Name': 'KEY_ID_COUNTER'}, {"$set":{'Value': current_id+1}},upsert = False)
        if not people.find_one({'email':str.lower(request_json['payLoad']['email'])},{'_id': False}) == None:
            response = jsonify([{
            }])
            response.status_code = 201
            print("duplicate")
            return response
        else:
            new_person = {
                'firstName': request_json['payLoad']['firstName'],
                'lastName': request_json['payLoad']['lastName'],
                'email': str.lower(request_json['payLoad']['email']),
                'password': request_json['payLoad']['password'],
                'familyName': str.lower(request_json['payLoad']['familyName']),
                'accountType': request_json['payLoad']['accountType'],
                'balance': 0
            }
            result1 = people.insert_one(new_person)
            creds = {
                'email': str.lower(request_json['payLoad']['email']),
                'password': request_json['payLoad']['password']
            }
            result2= credentials.insert_one(creds)
            print(new_person)
            response = jsonify([{
            }])
            response.status_code = 200
            return response

def findChildren(email, people):
    user = people.find_one({'email': str.lower(email)}, {'_id': False})
    if user == None:
        response = jsonify([{
        }])
        response.status_code=201
    else:
        childrenList = people.find({'familyName':str.lower(user['familyName'])},{'accountType':'Child'},{'_id': False})
        dictresponse = {}
        i = 0
        for child in childrenList:
            dictresponse[i]=child
            i = i+1
        response = jsonify(dictresponse)
        response.status_code = 200
    return response

def upBalance(request,people):
    request_json = request.get_json()
    user = people.find_one({'email': str.lower(request_json['payLoad']['email'])}, {'_id': False})
    if user == None:
        response = jsonify([{
        }])
        response.status_code=201
    else:
        lastbal = user['balance']
        people.update_one({'email': str.lower(user['email'])}, {"$set":{'balance': lastbal + request_json['payLoad']['increment']}},upsert = False)
        response = jsonify([{
        }])
        response.status_code=201
    return response
