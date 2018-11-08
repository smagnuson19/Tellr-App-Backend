from flask import Flask, request, jsonify

def handleCredentials(email, password, credentials):
    user = credentials.find_one({'email': email}, {'_id': False})
    if user == None:
        response = jsonify([{
        'Success': False,
        }])
        response.status_code = 201
    else:
        if user['password'] == password:
            response = jsonify([{
            'Success': True,
            }])
        else:
            response = jsonify([{
            'Success': False,
            }])
        response.status_code = 200
    return response
