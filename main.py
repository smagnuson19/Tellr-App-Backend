from pymongo import MongoClient
from flask import Flask, request, jsonify
from classes import *

app = Flask(__name__)

client1 = MongoClient('localhost', 27017)
db = client1.exampledb
credentials = db.credentials
people = db.people
families = db.families
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
            'name': request_json['loginInfo']['Name'],
            'email': request_json['loginInfo']['Email'],
            'balance': 0,
            'familyName': None
        }
        result1 = people.insert_one(new_person)
        creds = {
            'email': request_json['loginInfo']['Email'],
            'password': request_json['loginInfo']['Password'],
        }
    response = jsonify([{
    }])
    response.status_code = 200
    return response

@app.route("/api/users/<email>", methods =['GET'])
def get_user(email):
    if request.method == 'GET':
        user = people.find_one({'email': email},{'_id': False})
    response = jsonify(user)
    response.status_code = 200
    return response

@app.route("/api/<email>/credentials/<password>", methods =['GET'])
def check_credentials(email, password):
    if request.method == 'GET':
        user = credentials.find_one({'email': email}, {'_id': False})
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
        bills_post = people.find_one({'Name': 'John Smith'})
        print("hi")
        #here we would need to get items
        response = jsonify([{
        'Name': str(bills_post['Name']),
        'Children': str(bills_post['Children']),
        }])
        response.status_code = 200
    return response

if __name__ == "__main__":
    app.run()
