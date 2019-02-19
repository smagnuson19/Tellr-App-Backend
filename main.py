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
from push import *
from flask_mail import Mail, Message
import jwt
import onesignal as onesignal_sdk
import time
import datetime


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
# if MONGO_URL == None:
# MONGO_URL = "mongodb://localhost:27017"

onesignal_client = onesignal_sdk.Client(user_auth_key="MjhmY2U2ZWMtN2YyNy00MWRlLWI3ZmYtNGZmMDljMWM5MjM0",
                                        app={"app_auth_key": "MmVhODM2YjEtZjM4Mi00MzNjLWIxNmUtNjAwYzM2ZWYxNDZi", "app_id": "4e80c299-4fec-4279-bde3-3cdffbb24e1d"})

client1 = MongoClient(MONGO_URL)
db = client1.heroku_sxklq0jf
credentials = db.credentials
people = db.people
tasks = db.tasks
goals = db.goals
notifications = db.notifications
social = db.social
push_notifications = db.push_notifications
goal_last_posted = datetime.datetime.now()
# Task deadline notification checker - waiting for OneSignal account
# check_task_notis(tasks, push_notifications)

#Passed
@app.route("/api/childtasks/<email>", methods =['GET'])
def childtask_handler(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            return getTasksChild(fixEmail(email),tasks)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed
@app.route("/api/parenttasks/<familyName>", methods =['GET'])
def adulttask_handler(familyName):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            return getTasks(familyName,tasks)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/tasks", methods =['POST'])
def postTasks():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return postTask(request, tasks, people, notifications, mail, app, push_notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/tasks/completed", methods = ['POST'])
def completeTasks():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return completeTask(request, tasks, notifications, people, mail, app)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/tasks/seecompleted/<email>", methods = ['GET'])
def seeCompletedTasks():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            return getCompletedTasks(request, tasks)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/tasks/verified", methods = ['POST'])
def verifyTasks():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return verifyTask(request, tasks, notifications, people, mail, app, social, push_notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/users", methods =['POST'])
def add_users():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        return add_user(request, people, credentials, social)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/users/<email>", methods =['GET'])
def get_user(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
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
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/history/<email>", methods = ['GET'])
def getHistory():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            return getUserHistory(fixEmail(email), people)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/history/<email>/<timeframe>", methods = ['GET'])
def getTimedHistory():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            if str.lower(timeframe) == 'week':
                return getUserHistoryWeek(fixEmail(email), people)
            elif str.lower(timeframe) == 'month':
                return getUserHistoryMonth(fixEmail(email), people)
            elif str.lower(timeframe) == 'year':
                return getUserHistoryYear(fixEmail(email), people)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/auth/login", methods =['POST'])
def authenticate():
    if request.method == 'POST':
        return authenticateUser(request, credentials)

@app.route("/api/analytics/<email>/<timeframe>", methods = ['GET'])
def analyze():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            if str.lower(timeframe) == 'week':
                return getAnalyticsWeek(fixEmail(email), people)
            elif str.lower(timeframe) == 'month':
                return getAnalyticsMonth(fixEmail(email), people)
            elif str.lower(timeframe) == 'year':
                return getAnalyticsYear(fixEmail(email), people)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/auth/register", methods =['POST'])
def authregister():
    if request.method == 'POST':
        return authAddUser(request, people, credentials, social, push_notifications)

@app.route("/api/auth/changepassword", methods =['POST'])
def changePassword():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return authChangePassword(request, credentials)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/auth/forgotpassword", methods =['POST'])
def resetPassword():
    if request.method == 'POST':
        return forgotPassword(request, credentials, mail, app)
    else:
        response = jsonify([{
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/<email>/credentials/<password>", methods =['POST'])
def check_credentials(email, password):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return handleCredentials(email, password, credentials)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/goals/<email>", methods =['GET'])
def handleGoals(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            return getGoals(fixEmail(email), goals)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/goals/complete/<email>", methods =['GET'])
def handleCompleteGoals(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            return getCompleteGoals(fixEmail(email), goals)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/goals/incomplete/<email>", methods =['GET'])
def handleIncompleteGoals(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'GET':
            return getIncompleteGoals(fixEmail(email), goals)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/goals", methods =['POST'])
def makeGoals():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return postGoals(request, goals, people, notifications, mail, app)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/children/<email>", methods =['GET'])
def getChildren(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        realEmail = fixEmail(email)
        if request.method == 'GET':
            return findChildren(realEmail, people)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/balance", methods =['POST'])
def updateBalance():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return upBalance(request,people,notifications, mail, app)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/notifications/<email>", methods =['GET'])
def getNotifications(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        realEmail = fixEmail(email)
        if request.method == 'GET':
            return findNotifications(realEmail,notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/goals/approve", methods =['POST'])
def approveGoals():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return approveGoal(request, goals, people, notifications, mail, app, push_notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

#Passed Testing
@app.route("/api/redeem", methods =['POST'])
def redeemGoal():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return finishGoal(request,people, goals, notifications, mail, app, social)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/redeemmoney", methods =['POST'])
def redeemMoney():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return redeemMon(request,people, notifications, push_notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/notifications", methods =['POST'])
def updateNotifications():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return readNotifications(request, notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/deleteall", methods =['POST'])
def deleteAllUsers():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return deleteAllUser(request, people, credentials)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/delete", methods =['POST'])
def deleteOne():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return delOne(request, people, credentials)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/addfriend", methods =['POST'])
def addFriend():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return socialAdd(request, people, social, notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/acceptfriends", methods =['POST'])
def acceptFriend():
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        if request.method == 'POST':
            return socialAccept(request, people, social, notifications, push_notifications)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/social/<email>", methods =['GET'])
def getSocialStats(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        realEmail = fixEmail(email)
        if request.method == 'GET':
            return getStats(realEmail, people, social, tasks)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

@app.route("/api/social/taskhistory/<email>", methods =['GET'])
def getTaskHistory(email):
    authenStatus = verifyToken(request)
    if authenStatus[1]:
        realEmail = fixEmail(email)
        if request.method == 'GET':
            return get_completed_task_number_graph(email, social)
    else:
        response = jsonify([{'Error': authenStatus[0]
        }])
        response.status_code = 401
        return response

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
