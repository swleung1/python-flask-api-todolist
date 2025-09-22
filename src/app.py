"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

todos = [
    {"label": "Sample Todo 1", "done": True},
    {"label": "Sample Todo 2", "done": True},
]

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200

@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify(todos), 200

@app.route("/todos", methods=["POST"])
def add_todo():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    payload = request.get_json(silent=True) or {}
    label = payload.get("label")
    done = payload.get("done")

    if label is None or done is None:
        return jsonify({"error": "Fields 'label' (str) and 'done' (bool) are required"}), 400
    if not isinstance(label, str) or not isinstance(done, bool):
        return jsonify({"error": "'label' must be string and 'done' must be boolean"}), 400

    todos.append({"label": label, "done": done})
    return jsonify(todos), 201

@app.route("/todos/<int:position>", methods=["DELETE"])
def delete_todo(position):
    if position < 0 or position >= len(todos):
        return jsonify({"error": "Position out of range"}), 404
    todos.pop(position)
    return jsonify(todos), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
