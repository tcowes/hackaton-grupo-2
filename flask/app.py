from flask import Flask, request, Response, render_template
from database.db import initialize_db
from database.models import Content
from flask_restful import Api
from resources.routes import initialize_routes
from resources.errors import errors
from pymongo import MongoClient
from database.connection import MongoDB
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = Flask(__name__)
api = Api(app, errors=errors)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/titan'
}

initialize_db(app)
initialize_routes(api)

db = MongoDB().return_collection()
data = list(db.find({}))

@app.route('/deploy/content', methods=['GET'])
def show_all():
    return render_template('index.html', status=200, data=data)

app.run(debug=True)