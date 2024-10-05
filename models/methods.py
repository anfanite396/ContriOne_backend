from . import db
from .users import User, UserPlatform, Repo, Events
from ..services.requests import fetch_github, fetch_gitlab


def add_repo(username, platform, repo_id, repo_name, html_url):
    user_platform = UserPlatform.query.filter_by(username=username, platform=platform).first()

    # Check if repo already exists
    new_repo = Repo.query.filter_by(id=repo_id).first()
    if not new_repo:
        new_repo = Repo(id=repo_id, repo_name=repo_name, html_url=html_url, user_platform=user_platform)
        db.session.add(new_repo)
        db.session.commit()


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


def get_user_id_from_platform(username, platform):
    platform_fetchers = {
        "github": (fetch_github, "GH"),
        "gitlab": (fetch_gitlab, "GL"),
        # "gerrit": (None, "GR")
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


def add_platform(user_id, username, platform):
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


def add_user(name, username, email, hashed_password):
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


def delete_event(id):
    event = Events.query.get(id)
    if event:
        db.session.delete(event)
        db.session.commit()


def delete_repo(id):
    repo = Repo.query.get(id)
    if repo:
        for event in repo.events:
            cur_event = Events.query.get(event.id)
            if not cur_event:
                continue
            db.session.delete(cur_event)
        db.session.delete(repo)
        db.session.commit()


def delete_platform(id, user_id):
    platform = UserPlatform.query.filter_by(id=id, user_id=user_id).first()
    if platform:
        for repo in platform.repos:
            cur_repo = Repo.query.get(repo.id)
            if not cur_repo:
                continue

            for event in cur_repo.events:
                cur_event = Events.query.get(event.id)
                if not cur_event:
                    continue
                db.session.delete(cur_event)

            db.session.delete(cur_repo)

        db.session.delete(platform)
        db.session.commit()


def delete_user(id):
    user = User.query.get(id)
    if user:
        for platform in user.platforms:
            delete_platform(platform.id, user.id)
        db.session.delete(user)
        db.session.commit()