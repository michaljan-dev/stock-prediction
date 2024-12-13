from flask_restplus import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    jwt_refresh_token_required,
    get_jwt_identity,
)
from flask import g
from .models import User
from flask_allows import requires
from app import allows
from .utils import HasPermission
import datetime

parser = reqparse.RequestParser()
parser.add_argument("email", help="This field cannot be blank", required=True)
parser.add_argument("password", help="This field cannot be blank", required=True)


class UserRegistration(Resource):
    def post(self):
        return {"message": "User registration"}


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        user = User.query.filter_by(email=data["email"]).first()
        g.current_user = user
        allows.identity_loader(lambda: user)
        expires = datetime.timedelta(days=365)
        access_token_data = {
            "id": user.id,
            "username": user.username,
            "session": "session",
        }
        access_token = create_access_token(access_token_data, expires_delta=expires)
        refresh_token = create_access_token(access_token_data)
        return {
            "username": user.username,
            "token": access_token,
            "refresh_token": refresh_token,
        }


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {"access_token": access_token}


class UserLogout(Resource):
    def post(self):
        return {"message": "User logout"}


class AllUsers(Resource):
    @requires(HasPermission("users", "read"))
    def get(self):
        return {"message": "List of users"}

    def delete(self):
        return {"message": "Delete all users"}


class AclResource(Resource):
    def get(self):
        user = g.current_user
        permission = user.getResourcePermissions()
        return permission


class Test(Resource):
    def get(self):
        user = User.query.filter_by(username="admin").first()
        permission = user.getResourcePermissions()
        return permission

    def delete(self):
        return {"message": "Delete all users"}
