# API server entry
from flask import Blueprint
import logging
import os

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/')
def index():
    return "Welcome to the PyBins API"

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(api_blueprint)
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))