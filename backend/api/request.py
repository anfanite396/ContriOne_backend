from flask import jsonify, session, make_response, request, current_app
from flask_restful import Resource
import json

from .login import login_required
from ..models.users import Repo, Events, User, UserPlatform
from ..models.methods import add_platform, delete_platform
from ..services.tasks import update_user


class RepoData(Resource):
    def get(self, username):
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return make_response(jsonify({"error" : "User not found"}), 404)

            user_platforms = UserPlatform.query.filter_by(user_id=user.id).all()
            repo_data = []

            for platform in user_platforms:
                # Fetch all the repositories
                repos = Repo.query.filter_by(user_platform_id=platform.id).all()
                for repo in repos:
                    repo_data.append({
                        "repo_id" : repo.id,
                        "repo_name" : repo.repo_name,
                        "html_url" : repo.html_url,
                        "platform" : platform.platform
                    })
            
            return make_response(jsonify({"repos" : repo_data}), 200)
        except Exception as e:
            current_app.logger.error(f"Error while fetching repositories : {e}")
            return make_response(jsonify({"error": "Internal server error"}), 500)


class UserData(Resource):
    def get(self, username):
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return make_response(jsonify({"error": "User not found"}), 404)
            
            platforms = [
                {
                    "id": platform.id,
                    "platform": platform.platform,
                    "username": platform.username
                }
                for platform in user.platforms
            ]
            return make_response(jsonify({
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'platforms': platforms
            }), 200)
        
        except Exception as e:
            current_app.logger.error(f"Error fetching user data for {username}: {e}")
            return make_response(jsonify({"error": "Internal server error"}), 500)


class EventData(Resource):
    def get(self, username):
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return make_response(jsonify({"error": "User not found"}), 404)

            user_platforms = UserPlatform.query.filter_by(user_id=user.id).all()
            event_data = []

            for platform in user_platforms:
                # Fetch all the repositories
                repos = Repo.query.filter_by(user_platform_id=platform.id).all()

                for repo in repos:
                    # Fetch events for each repository
                    events = Events.query.filter_by(repo_id=repo.id).all()
                    if events:
                        data = [
                            {
                                "event_id": event.id,
                                "type": event.type,
                                "created_at": event.created_at,
                                "html_url": repo.html_url,
                                "platform": platform.platform,
                            }
                            for event in events
                        ]
                        event_data.append(data)

            return make_response(jsonify({"events": event_data}), 200)
        
        except Exception as e:
            current_app.logger.error(f"Error fetching events for {username}: {e}")
            return make_response(jsonify({"error": "Internal server error"}), 500)


class UpdateUserData(Resource):
    @login_required
    def post(self, username):
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return make_response(jsonify({"error" : "User not found"}), 404)
            
            loggedInUser = session.get("user_id")
            if loggedInUser != user.id:
                return make_response(jsonify({"error" : "Authentication failure"}, 401))
            update_user(user.id)

            return make_response(jsonify({"message" : "User updated."}, 201))
        except Exception as e:
            current_app.logger.error(f"Error updating events for {username} : {e}")
            return make_response(jsonify({"error": "Internal server error"}), 500)
    

class AddPlatform(Resource):
    @login_required
    def post(self, username):
        try:
            data = request.get_json()
            platform = data.get('platform')
            platform_username = data.get('username')
            user_id = session.get("user_id")
            user = User.query.filter_by(username=username).first()

            if user.id != user_id:
                return make_response(jsonify({"error" : "Authentication failed"}), 401)

            if not user:
                return make_response(jsonify({"error" : "Failed"}), 400)
            status = add_platform(user.id, platform_username, platform)

            if status == "Success":
                update_user(user_id)
                return make_response(jsonify({"message" : "Platform successfully added"}, 201))
            return make_response(jsonify({"error" : status}), 400)
        except Exception as e:
            current_app.logger.error(f"Error while adding platform for {username} : {e}")
            return make_response(jsonify({"error": "Internal server error"}), 500)

class RemovePlatform(Resource):
    @login_required
    def post(self, username):
        data = request.get_json()
        platform = data.get('platform')

        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return make_response(jsonify({"error" : "No such user"}), 400)
            
            user_platform = UserPlatform.query.filter_by(platform=platform, user_id=user.id).first()

            if not user_platform:
                return make_response(jsonify({"error" : "User platform does not exist"}), 404)
            
            delete_platform(user_platform.id, user.id)
            return make_response(jsonify({"message" : "Platform successfully deleted"}), 201)
        except Exception as e:
            print(f"Error while removing user platform : {e}")
            return make_response(jsonify({"error" : e}), 500)
        


