from pymongo import MongoClient
from flask import Flask, request, jsonify
from users import *
from tasks import *
from credentials import *
from goals import *
import string

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
        return getTasksChild(email,tasks)

@app.route("/api/parenttasks/<familyName>", methods =['GET'])
def adulttask_handler(familyName):
    if request.method == 'GET':
        return getTasks(familyName,tasks)

@app.route("/api/tasks", methods =['POST'])
def postTasks():
    if request.method == 'POST':
        return postTask(request, familyName, tasks)

@app.route("/api/users", methods =['POST'])
def add_users():
    return add_user(request, people, credentials)

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

@app.route("/api/<email>/credentials/<password>", methods =['POST'])
def check_credentials(email, password):
    if request.method == 'POST':
        return handleCredentials(email, password, credentials)

@app.route("/api/goals/<email>", methods =['GET', 'POST'])
def handleGoals(email):
    if request.method == 'GET':
        return getGoals(email, goals)
    if request.method == 'POST':
        return postGoals(request, email, goals)

@app.route("/api/children/<email>", methods =['GET'])
def getChildren(email):
    if request.method == 'GET':
        return getChildren(email, people)

@app.route("/api/balance", methods =['POST'])
def updateBalance():
    if request.method == 'POST':
        return upBalance(request,people)

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
