from flask import Flask, request, jsonify

#Deprecated after authentication
def handleCredentials(email, password, credentials):
    user = credentials.find_one({'email': str.lower(email)}, {'_id': False})
    if user == None:
        response = jsonify([{
        'Success': False,
        'Error' : 'Incorrect username and password combo',
        }])
        response.status_code = 401
        print('Nope')
    else:
        if user['password'] == password:
            response = jsonify([{
            'Success': True,
            }])
            print('Success')
            response.status_code = 200
        else:
            response = jsonify([{
            'Success': False,
            'Error' : 'Incorrect password',
            }])
            print('Nope')
            response.status_code = 401

    return response
