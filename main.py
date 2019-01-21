from pymongo import MongoClient
from flask import Flask, request, jsonify
from users import *
from tasks import *
from credentials import *
from goals import *
from notification import *
from handleEmail import *
from authenticate import *
from social import *
import string
from flask_mail import Mail, Message
import jwt

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME = 'tellr.notifications@gmail.com',
    MAIL_PASSWORD = 'tellr12345'
    )
mail = Mail(app)

MONGO_URL = 'mongodb://heroku_sxklq0jf:fvegd2q34of2qn0j5jivm9b51b@ds227243.mlab.com:27243/heroku_sxklq0jf'
if MONGO_URL == None:
    MONGO_URL = "mongodb://localhost:27017";


client1 = MongoClient(MONGO_URL)
db = client1.heroku_sxklq0jf
credentials = db.credentials
people = db.people
tasks = db.tasks
goals = db.goals
notifications = db.notifications
social = db.social

#Passed
@app.route("/api/childtasks/<email>", methods =['GET'])
def childtask_handler(email):
    if request.method == 'GET':
        return getTasksChild(fixEmail(email),tasks)

#Passed
@app.route("/api/parenttasks/<familyName>", methods =['GET'])
def adulttask_handler(familyName):
    if request.method == 'GET':
        return jwt.encode(getTasks(familyName,tasks), secret, algorithms=['HS256'])

#Passed Testing
@app.route("/api/tasks", methods =['POST'])
def postTasks():
    if request.method == 'POST':
        return postTask(request, tasks, people, notifications, mail, app)

#Passed Testing
@app.route("/api/tasks/completed", methods = ['POST'])
def completeTasks():
    if request.method == 'POST':
        return completeTask(request, tasks, notifications, people, mail, app)

#Passed Testing
@app.route("/api/tasks/verified", methods = ['POST'])
def verifyTasks():
    if request.method == 'POST':
        return verifyTask(request, tasks, notifications, people, mail, app)

#Passed Testing
@app.route("/api/users", methods =['POST'])
def add_users():
    return add_user(request, people, credentials)

#Passed Testing
@app.route("/api/users/<email>", methods =['GET'])
def get_user(email):
    realEmail=fixEmail(email)
    if request.method == 'GET':
        user = people.find_one({'email': realEmail},{'_id': False})
        print(user)
    if user == None:
        response = jsonify([{
        }])
        response.status_code = 202
    else:
        response = jsonify(user)
        response.status_code = 200
    return response

@app.route("/api/auth/login", methods =['POST'])
def authenticate():
    if request.method == 'POST':
        return authenticateUser(request, credentials)

@app.route("/api/auth/register", methods =['POST'])
def authregister():
    if request.method == 'POST':
        return authAddUser(request, credentials)

@app.route("/api/auth/changepassword", methods =['POST'])
def changePassword():
    if request.method == 'POST':
        return authChangePassword(request, credentials)

@app.route("/api/auth/forgotpassword", methods =['POST'])
def resetPassword():
    if request.method == 'POST':
        return forgotPassword(request, credentials, mail, app)

#Passed Testing
@app.route("/api/<email>/credentials/<password>", methods =['POST'])
def check_credentials(email, password):
    if request.method == 'POST':
        return handleCredentials(email, password, credentials)

#Passed Testing
@app.route("/api/goals/<email>", methods =['GET'])
def handleGoals(email):
    if request.method == 'GET':
        return getGoals(fixEmail(email), goals)

#Passed Testing
@app.route("/api/goals", methods =['POST'])
def makeGoals():
    if request.method == 'POST':
        return postGoals(request, goals, people, notifications, mail, app)

#Passed Testing
@app.route("/api/children/<email>", methods =['GET'])
def getChildren(email):
    realEmail = fixEmail(email)
    if request.method == 'GET':
        return findChildren(realEmail, people)

#Passed Testing
@app.route("/api/balance", methods =['POST'])
def updateBalance():
    if request.method == 'POST':
        return upBalance(request,people,notifications, mail, app)

#Passed Testing
@app.route("/api/notifications/<email>", methods =['GET'])
def getNotifications(email):
    realEmail = fixEmail(email)
    if request.method == 'GET':
        return findNotifications(realEmail,notifications)

@app.route("/api/goals/approve", methods =['POST'])
def approveGoals():
    if request.method == 'POST':
        return approveGoal(request, goals, people, notifications, mail, app)

#Passed Testing
@app.route("/api/redeem", methods =['POST'])
def redeemGoal():
    if request.method == 'POST':
        return finishGoal(request,people, goals, notifications, mail, app)

@app.route("/api/redeemmoney", methods =['POST'])
def redeemMoney():
    if request.method == 'POST':
        return redeemMon(request,people, notifications)

@app.route("/api/notifications", methods =['POST'])
def updateNotifications():
    if request.method == 'POST':
        return readNotifications(request, notifications)

@app.route("/api/deleteall", methods =['POST'])
def deleteAllUsers():
    if request.method == 'POST':
        return deleteAllUser(request, people, credentials)

@app.route("/api/delete", methods =['POST'])
def deleteOne():
    if request.method == 'POST':
        return delOne(request, people, credentials)

@app.route("/api/addfriend", methods =['POST'])
def addFriend():
    if request.method == 'POST':
        return socialAdd(request, people, social)

@app.route("/api/acceptfriends", methods =['POST'])
def acceptFriend():
    if request.method == 'POST':
        return socialAccept(request, people, social)

@app.route("/api/", methods =['GET', 'POST'])
def main():
    if request.method == 'POST':
        request_json = request.get_json()
        print(request_json)
        response = jsonify([{
        }])
        response.status_code = 200
    if request.method == 'GET':
        response = jsonify([{'URL': MONGO_URL
        }])
        response.status_code = 200
    return response

if __name__ == "__main__":
    app.run()
