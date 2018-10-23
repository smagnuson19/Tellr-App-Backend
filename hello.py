from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/api/", methods =['GET'])
def hello():
    if request.method == 'GET':
        #here we would need to get items
        response = jsonify({
        'id': '2332',
        'name': 'Barbra',
        })
        response.status_code = 200
    return response
# main area

if __name__ == "__main__":
    app.run()
