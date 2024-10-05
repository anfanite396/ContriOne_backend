from flask import request, jsonify, session, make_response, current_app
from flask_restful import Resource
from functools import wraps
import bcrypt, secrets

from ..models.users import db, User
from ..models.methods import add_event, add_repo, add_platform, add_user
from ..services.tasks import update_user


class Register(Resource):
    def post(self):
        data = request.get_json()

        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes, salt)

        status = add_user(name, username, email, hashed_password)
        if status == "Success":
            return make_response(jsonify({"message" : "User created successfully"}), 201)
        return make_response(jsonify({"error" : status}), 400)
    

class Login(Resource):
    def post(self):
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user:
            return make_response(jsonify({"error" : "User does not exist"}), 404)

        if (bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))):
            session.clear()
            session["user_id"] = user.id
            response = make_response(jsonify({"message": "Logged in successfully"}), 200)
            
            # Generate a dynamic session ID
            session_id = secrets.token_hex(16)
            
            # Set the cookie with correct attributes
            response.set_cookie(
                'session',
                session_id,
                httponly=True,
                secure=True,  # Set to True for HTTPS
                samesite='None',
                max_age=3600  # 1 hour expiration, adjust as needed
            )
            
            return response
        else:
            return make_response(jsonify({"error" : "Invalid password"}), 401)


class Logout(Resource):
    def post(self):
        try:
            user_id = session.get('user_id')
            if user_id:
                session.pop('user_id', None)
                return make_response(jsonify({"message": "Successfully logged out"}), 200)
            else:
                return make_response(jsonify({"message": "No user logged in"}), 400)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return make_response(jsonify({"error" : "User not logged in"}), 401)
        return f(*args, **kwargs)
    return decorated_function
