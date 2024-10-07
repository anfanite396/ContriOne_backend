from flask import request, jsonify, session, make_response, current_app
from flask_restful import Resource
from functools import wraps
import bcrypt

from ..models.users import User
from ..models.methods import add_user


class Register(Resource):
    def post(self):
        try:
            data = request.get_json()

            if not data:
                return make_response(jsonify({"error": "Invalid input data"}), 400)

            name = data.get('name')
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not all([name, username, email, password]):
                return make_response(jsonify({"error": "All fields are required"}), 400)

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # Add the user to the database
            status = add_user(name, username, email, hashed_password)
            if status == "Success":
                session.clear()
                user = User.query.filter_by(username=username).first()
                if user:
                    session["user_id"] = user.id
                return make_response(jsonify({"message": "User created successfully"}), 201)
            return make_response(jsonify({"error": status}), 400)
        
        except Exception as e:
            current_app.logger.error(f"Error during registration: {e}")
            return make_response(jsonify({"error": "Internal server error"}), 500)


class Login(Resource):
    def post(self):
        try:
            username = request.form.get("username")
            password = request.form.get("password")

            if not username or not password:
                return make_response(jsonify({"error": "Username and password are required"}), 400)

            user = User.query.filter_by(username=username).first()
            if not user:
                return make_response(jsonify({"error": "User does not exist"}), 404)

            # Check the password
            if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                session.clear()
                session["user_id"] = user.id
                return make_response(jsonify({"message": "Logged in successfully"}), 200)
            else:
                return make_response(jsonify({"error": "Invalid password"}), 401)
        
        except Exception as e:
            current_app.logger.error(f"Error during login: {e}")
            return make_response(jsonify({"error": "Internal server error"}), 500)


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
