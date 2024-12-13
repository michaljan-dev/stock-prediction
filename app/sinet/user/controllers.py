from flask import Blueprint
from app import api, app
from . import resources

# Define the blueprint:
url_prefix = "/sinet/user"

sinet_user = Blueprint("sinet_user", __name__, url_prefix)
app.register_blueprint(sinet_user)

# REST resources
api.add_resource(resources.UserRegistration, url_prefix + "/auth/registration")
api.add_resource(resources.UserLogin, url_prefix + "/auth/login")
api.add_resource(resources.TokenRefresh, url_prefix + "/auth/token/refresh")
api.add_resource(resources.UserLogout, url_prefix + "/auth/logout")
api.add_resource(resources.AclResource, url_prefix + "/auth/acl")

api.add_resource(resources.AllUsers, url_prefix + "/users")
api.add_resource(resources.Test, url_prefix + "/test")
