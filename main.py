from pymongo import MongoClient
from flask import Flask, request, jsonify
from classes import *

app = Flask(__name__)

client1 = MongoClient('localhost', 27017)
db = client1.exampledb
credentials = db.credentials
people = db.people
tasks = db.tasks
goals = db.goals

KEY_ID_COUNTER= {
    'Name': 'KEY_ID_COUNTER',
    'Value': 100000
}
TEST_GOAL={
    'Name': 'Test',
    'ID': 100001
}
people.insert_one(KEY_ID_COUNTER)
goals.insert_one(TEST_GOAL)

@app.route("/api/childtasks/<email>", methods =['GET'])
def childtask_handler(email):
    if request.method == 'GET':
        tasksList = tasks.find({'recEmail':email},{'_id': False})
        dictresponse = {}
        i = 0
        for task in tasksList:
            dictresponse[i]=task
            i = i+1
        response = jsonify(dictresponse)
        response.status_code = 200
        return response

@app.route("/api/parenttasks/<familyName>", methods =['POST','GET'])
def adulttask_handler(familyName):
    if request.method == 'GET':
        tasksList = tasks.find({'familyName':familyName},{'_id': False})
        dictresponse = {}
        i = 0
        for task in tasksList:
            dictresponse[i]=task
            i = i+1
        response = jsonify(dictresponse)
        response.status_code = 200
        return response

    if request.method == 'POST':
        request_json = request.get_json()
        new_task = {
            'name': request_json['taskInfo']['name'],
            'value': request_json['taskInfo']['value'],
            'deadline': request_json['taskInfo']['deadline'],
            'description': request_json['taskInfo']['description'],
            'recEmail': request_json['taskInfo']['recEmail'],
            'complete': request_json['taskInfo']['complete'],
            'dateCompleted': request_json['taskInfo']['dateCompleted'],
            'familyName':request_json['taskInfo']['familyName']
        }
        result1 = tasks.insert_one(new_task)
        response = jsonify([{
        }])
        response.status_code = 200
        return response

@app.route("/api/users", methods =['POST'])
def add_users():
    if request.method == 'POST':
        request_json = request.get_json()
        # people.update_one({'Name': 'KEY_ID_COUNTER'}, {"$set":{'Value': current_id+1}},upsert = False)
        new_person = {
            'firstName': request_json['payLoad']['firstName'],
            'lastName': request_json['payLoad']['lastName'],
            'email': request_json['payLoad']['email'],
            'password': request_json['payLoad']['password'],
            'familyName': request_json['payLoad']['familyName'],
            'accountType': request_json['payLoad']['accountType'],
            'balance': 0
        }
        result1 = people.insert_one(new_person)
        creds = {
            'email': request_json['payLoad']['email'],
            'password': request_json['payLoad']['password']
        }
    print(new_person)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

@app.route("/api/users/<email>", methods =['GET'])
def get_user(email):
    if request.method == 'GET':
        user = people.find_one({'email': email},{'_id': False})
    if user == None:
        response = jsonify([{
        }])
        response.status_code = 202
    else:
        response = jsonify(user)
        response.status_code = 200
    return response

@app.route("/api/<email>/credentials/<password>", methods =['GET'])
def check_credentials(email, password):
    if request.method == 'GET':
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

@app.route("/api/goals/<email>", methods =['GET', 'POST'])
def handleGoals(email):
    if request.method == 'GET':
        goalList = goals.find({'email': email},{'_id': False})
        dictresponse = {}
        i = 0
        for goal in goalList:
            dictresponse[i]=goal
            i = i+1
        response = jsonify(dictresponse)
        response.status_code = 200
        return response
    if request.method == 'POST':
        request_json = request.get_json()
        new_goal = {
            'Name': request_json['goalInfo']['Name'],
            'Prize': request_json['goalInfo']['Prize'],
            'ID': id,
            'Description': request_json['goalInfo']['Description']
        }
        result = goals.insert_one(new_goal)

@app.route("/api/children/<email>", methods =['GET'])
def getChildren(email):
    if request.method == 'GET':
        user = people.find_one({'email': email}, {'_id': False})
        if user == None:
            response = jsonify([{
            }])
            response.status_code=201
        else:
            childrenList = people.find({'familyName':user['familyName']},{'accountType':'Child'},{'_id': False})
            dictresponse = {}
            i = 0
            for child in childrenList:
                dictresponse[i]=child
                i = i+1
            response = jsonify(dictresponse)
            response.status_code = 200
        return response

@app.route("/api/balance", methods =['POST'])
def updateBalance():
    if request.method == 'POST':
        request_json = request.get_json()
        user = people.find_one({'email': request_json['payLoad']['email']}, {'_id': False})
        if user == None:
            response = jsonify([{
            }])
            response.status_code=201
        else:
            lastbal = user['balance']
            people.update_one({'email': user['email']}, {"$set":{'balance': lastbal + request_json['payLoad']['increment']}},upsert = False)
            response = jsonify([{
            }])
            response.status_code=201
        return response

@app.route("/api/", methods =['GET', 'POST'])
def main():
    if request.method == 'POST':
        # main area
        request_json = request.get_json()
        #here we would need to get item
        print(request_json)
        response = jsonify([{
        }])
        response.status_code = 200
    if request.method == 'GET':
        response = jsonify([{
        # 'Name': str(bills_post['Name']),
        # 'Children': str(bills_post['Children']),
        }])
        response.status_code = 200
    return response

if __name__ == "__main__":
    app.run()
