from flask import Blueprint
from flask_restful import Api

from .login import Login, Logout, Register
from .request import RepoData, UserData, EventData, UpdateUserData, AddPlatform, RemovePlatform


api_bp = Blueprint("api_bp", __name__)
api = Api(api_bp)

api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(Register, "/register")
api.add_resource(UserData, "/<string:username>")
api.add_resource(RepoData, "/<string:username>/repos")
api.add_resource(EventData, "/<string:username>/events")
api.add_resource(UpdateUserData, "/<string:username>/update-user")
api.add_resource(AddPlatform, "/<string:username>/add-platform")
api.add_resource(RemovePlatform, "/<string:username>/remove-platform")