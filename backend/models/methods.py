from flask import current_app

from . import db
from .users import User, UserPlatform, Repo, Events
from ..services.requests import fetch_github, fetch_gitlab


def add_event(repo_id, id, type, created_at):
    # Check if Event already exists
    new_event = Events.query.filter_by(id=id).first()
    if not new_event:
        repo = Repo.query.get(repo_id)
        if not repo:
            return "Repo does not exist"
        new_event = Events(id=id, type=type, created_at=created_at, repo_id=repo_id)
        db.session.add(new_event)
        db.session.commit()


def add_repo(username, platform, repo_id, repo_name, html_url):
    try:
        user_platform = UserPlatform.query.filter_by(username=username, platform=platform).first()

        # Check if repo already exists
        new_repo = Repo.query.filter_by(id=repo_id).first()
        if not new_repo:
            new_repo = Repo(id=repo_id, repo_name=repo_name, html_url=html_url, user_platform=user_platform)
            db.session.add(new_repo)
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error adding repository: {e}")


def get_user_id_from_platform(username, platform):
    try:
        platform_fetchers = {
            "github": (fetch_github, "GH"),
            "gitlab": (fetch_gitlab, "GL"),
        }

        fetcher_info = platform_fetchers.get(platform)

        if not fetcher_info:
            return "Invalid platform"

        fetch_function, prefix = fetcher_info

        # Fetch data for the specific platform
        user_data = fetch_function(username)

        if not user_data or 'id' not in user_data:
            return None
        user_id = user_data['id']
        return f"{prefix}{user_id}"
    except Exception as e:
        current_app.logger.error(f"Error fetching user ID from {platform}: {e}")
        return None


def add_platform(user_id, username, platform):
    try:
        user = User.query.filter_by(id=user_id).one_or_none()
        if not user:
            return "User not found"
        
        existing_platform = UserPlatform.query.filter_by(username=username, platform=platform).first()
        if existing_platform:
            return "User platform already exists"
        
        id = get_user_id_from_platform(username, platform)
        if not id:
            return "Username not found on platform"

        new_platform = UserPlatform(id=id, username=username, platform=platform, user=user)
        db.session.add(new_platform)
        db.session.commit()

        return "Success"
    except Exception as e:
        current_app.logger.error(f"Error adding platform {platform} for user {username}: {e}")
        return f"Failed to add platform due to {e}"


def add_user(name, username, email, hashed_password):
    try:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists"
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already in use"
        
        new_user = User(name=name, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return "Success"
    except Exception as e:
        current_app.logger.error(f"Error adding user {username}: {e}")
        return f"Failed to add user due to {e}"


def delete_event(id):
    try:
        event = Events.query.get(id)
        if event:
            db.session.delete(event)
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error deleting event with ID {id}: {e}")


def delete_repo(id):
    try:
        repo = Repo.query.get(id)
        if repo:
            for event in repo.events:
                cur_event = Events.query.get(event.id)
                if cur_event:
                    db.session.delete(cur_event)
            db.session.delete(repo)
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error deleting repository with ID {id}: {e}")

def delete_platform(id, user_id):
    try:
        platform = UserPlatform.query.filter_by(id=id, user_id=user_id).first()
        if platform:
            for repo in platform.repos:
                cur_repo = Repo.query.get(repo.id)
                if cur_repo:
                    for event in cur_repo.events:
                        cur_event = Events.query.get(event.id)
                        if cur_event:
                            db.session.delete(cur_event)
                    db.session.delete(cur_repo)
            db.session.delete(platform)
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error deleting platform with ID {id}: {e}")


def delete_user(id):
    try:
        user = User.query.get(id)
        if user:
            for platform in user.platforms:
                delete_platform(platform.id, user.id)
            db.session.delete(user)
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error deleting user with ID {id}: {e}")
