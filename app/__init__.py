# Import flask and template operators
from flask import Flask

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_allows import Allows
from flask_jwt_extended import JWTManager
from flask_restplus import Api

# Define the application object
app = Flask(__name__)

# Configurations
app.config.from_object("config")
cors = CORS(app, resources=app.config.get("CORS_RESOURCES"))

# Permission
allows = Allows(app)

# Json token declaration
jwt = JWTManager(app)

# Define the database object which is imported by modules and controllers
db = SQLAlchemy(app)

# Api rest
api = Api(app)

# Modules
# Import the core module responsible for loading the logic of all other modules.
from app.sinet.core.controllers import sinet_core

# This will create the database file using SQLAlchemy
db.create_all()
