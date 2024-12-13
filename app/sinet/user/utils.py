from .models import User
from app import app, allows
from flask import abort, g
from flask_jwt_extended import decode_token
from flask_allows import Requirement


@app.before_request
def before_request_guard():
    from flask import request

    auth_path_skip = ["user_login", "graphql", "test"]
    #     request.method
    if request.endpoint not in auth_path_skip:

        if "Authorization" in request.headers:
            jwt_token = request.headers.get("Authorization", None)
            if jwt_token:
                parts = jwt_token.split()
                if parts[0].lower() != "bearer":
                    abort(401)
                else:
                    jwt_token_decoded = decode_token(parts[1])
                    #                     return jwt_token_decoded
                    username = jwt_token_decoded["identity"]["username"]
                    user = User.query.filter_by(username=username).first()
                    if user:
                        g.current_user = user
                        allows.identity_loader(lambda: user)
                        #                        print(user.username)
                        #                        print(jwt_token_decode)
                        return None
                    else:
                        abort(401)
        else:
            abort(401)


class HasPermission(Requirement):
    def __init__(self, resource, permission):
        self.permission = permission
        self.resource = resource

    def fulfill(self, user):
        resource_permissions = user.getResourcePermissions()
        # return self.permission in user.permissions
        return True


class HasRole(Requirement):
    def __init__(self, permission):
        self.permission = permission

    def fulfill(self, user):
        return self.permission in user.permissions
