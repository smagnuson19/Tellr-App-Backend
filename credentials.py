from flask import Flask, request, jsonify

def handleCredentials(email, password, credentials):
    user = credentials.find_one({'email': str.lower(email)}, {'_id': False})
    if user == None:
        response = jsonify([{
        'Success': False,
        }])
        response.status_code = 201
        print('Nope')
    else:
        if user['password'] == password:
            response = jsonify([{
            'Success': True,
            }])
            print('Success')
        else:
            response = jsonify([{
            'Success': False,
            }])
            print('Nope')
        response.status_code = 200
    return response
