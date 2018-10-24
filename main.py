from pymongo import MongoClient
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/", methods =['GET', 'POST'])
def main():
    client1 = MongoClient('localhost', 27017)
    db = client1.exampledb
    people = db.people
    people_data = {
        'Name': 'John Smith',
        'Adult': True,
        'Children': ['Johnny Smith, John Jr. Smith'],
        'ID': '00001'
    }
    result = people.insert_one(people_data)
    print('One person: {0}'.format(result.inserted_id))

    if request.method == 'GET':
        bills_post = people.find_one({'Name': 'John Smith'})
        #here we would need to get items
        response = jsonify([{
        'Name': str(bills_post['Name']),
        'Children': str(bills_post['Children']),
        }])
        print("Method 1")
        response.status_code = 200
    # main area

    if request.method == 'POST':
        print("Method 2")
        request_json = request.get_json()
        #here we would need to get items
        value1 = request_json.get('id')
        value2= request_json.get('name')

        response = jsonify([{'status':'done'}])
        response.status_code=200
    return response

if __name__ == "__main__":
    app.run()
