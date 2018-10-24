from pymongo import MongoClient
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/", methods =['GET'])
def main():
    client1 = MongoClient('localhost', 27017)
    db = client1.exampledb
    people = db.people
    people_data = {
        'title': 'Python and MongoDB',
        'content': 'PyMongo is fun, you guys',
        'author': 'Scott'
    }
    result = people.insert_one(people_data)
    print('One person: {0}'.format(result.inserted_id))

    if request.method == 'GET':
        bills_post = people.find_one({'author': 'Scott'})
        #here we would need to get items
        response = jsonify([{
        'id': str(bills_post['title']),
        'name': str(bills_post['author']),
        }])
        response.status_code = 200
    return response
    # main area

if __name__ == "__main__":
    app.run()
