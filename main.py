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
people.insert_one(KEY_ID_COUNTER)

@app.route("/api/users", methods =['POST'])
def add_users():
    if request.method == 'POST':
        request_json = request.get_json()
        id_counter = people.find_one({'Name': 'KEY_ID_COUNTER'})
        current_id = id_counter['Value']
        people.update_one({'Name': 'KEY_ID_COUNTER'}, {"$set":{'Value': current_id+1}},upsert = False)
        new_person = {
            'Name': request_json['loginInfo']['Name'],
            'Email': request_json['loginInfo']['Email'],
            'ID': current_id
        }
        print(new_person)
        result1 = people.insert_one(new_person)
        creds = {
            'Username': request_json['loginInfo']['Username'],
            'Password': request_json['loginInfo']['Password'],
            'ID': current_id
        }
        result2 = credentials.insert_one(creds)
    response = jsonify([{
    }])
    response.status_code = 200
    return response

@app.route("/api/users/<int:id>", methods =['GET'])
def get_user(id):
    if request.method == 'GET':
        user = people.find_one({'ID': id},{'_id': False})
    print(user)
    response = jsonify(user)
    response.status_code = 200
    return response

@app.route("/api/<username>/credentials/<password>", methods =['GET'])
def check_credentials(username, password):
    if request.method == 'GET':
        user = credentials.find_one({'Username': username}, {'_id': False})
        if user['password'] == Password:
            response = jsonify([{
            'Success': True,
            'ID': user['ID']
            }])
        else:
            response = jsonify([{
            'Success': False,
            'ID': None
            }])
        response.status_code = 200
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
