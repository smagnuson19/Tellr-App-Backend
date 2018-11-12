from pymongo import MongoClient
from flask import Flask, request, jsonify
from users import *
from tasks import *
from credentials import *
from goals import *
from notification import *
import string

app = Flask(__name__)

client1 = MongoClient('localhost', 27017)
db = client1.exampledb
credentials = db.credentials
people = db.people
tasks = db.tasks
goals = db.goals
notifications = db.notifications

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
        return postTask(request, tasks, people, notifications)

@app.route("/api/tasks/completed", methods = ['POST'])
def completeTasks():
    if request.method == 'POST':
        return completeTask(request, tasks, notifications, people)

@app.route("/api/tasks/verified", methods = ['POST'])
def verifyTasks():
    if request.method == 'POST':
        return verifyTask(request, tasks, notifications, people)

@app.route("/api/users", methods =['POST'])
def add_users():
    return add_user(request, people, credentials)

@app.route("/api/users/<email>", methods =['GET'])
def get_user(email):
    realEmail=str.lower(email)
    if request.method == 'GET':
        user = people.find_one({'email': realEmail},{'_id': False})
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

@app.route("/api/goals/<email>", methods =['GET'])
def handleGoals(email):
    if request.method == 'GET':
        return getGoals(email, goals)

@app.route("/api/goals", methods =['POST'])
def makeGoals():
    if request.method == 'POST':
        return postGoals(request, goals, people, notifications)

@app.route("/api/children/<email>", methods =['GET'])
def getChildren(email):
    realEmail = email[1:-1]
    if request.method == 'GET':
        return findChildren(realEmail, people)

@app.route("/api/balance", methods =['POST'])
def updateBalance():
    if request.method == 'POST':
        return upBalance(request,people,notifications)

@app.route("/api/notifications/<email>", methods =['GET'])
def getNotifications(email):
    realEmail = email[1:-1]
    if request.method == 'GET':
        return findNotifications(realEmail,notifications,people)

@app.route("/api/redeem", methods =['POST'])
def redeemGoal():
    if request.method == 'POST':
        return finishGoal(request,people, goals, notification)

@app.route("/api/", methods =['GET', 'POST'])
def main():
    if request.method == 'POST':
        request_json = request.get_json()
        print(request_json)
        response = jsonify([{
        }])
        response.status_code = 200
    if request.method == 'GET':
        response = jsonify([{
        }])
        response.status_code = 200
    return response

if __name__ == "__main__":
    app.run()
