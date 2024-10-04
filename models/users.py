from flask_sqlalchemy import SQLAlchemy

from ..services.requests import fetch_github, fetch_gitlab

db = SQLAlchemy()


class Repo(db.Model):
    __tablename__ = 'repo'  # Explicitly define table name
    id = db.Column(db.String(63), primary_key=True)  # Keep as String
    repo_name = db.Column(db.String(255), nullable=False)
    html_url = db.Column(db.String(1023), nullable=False)

    user_platform_id = db.Column(db.String(255), db.ForeignKey('user_platform.id'), nullable=False)
    events = db.relationship('Events', backref='repo', lazy=True)


class Events(db.Model):
    __tablename__ = 'events'  # Explicitly define table name
    id = db.Column(db.String(63), primary_key=True)  # Keep as String
    type = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    repo_id = db.Column(db.String(63), db.ForeignKey('repo.id'))  # Change to String to match Repo's id


class UserPlatform(db.Model):
    __tablename__ = 'user_platform'  # Explicitly define table name
    id = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    last_modified = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repos = db.relationship('Repo', backref='user_platform', lazy=True)


class User(db.Model):
    __tablename__ = 'user'  # Explicitly define table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(255), nullable=False)
    platforms = db.relationship('UserPlatform', backref='user', lazy=True)


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

def delete_event(id):
    event = Events.query.get(id)
    if event:
        db.session.delete(event)
        db.session.commit()

def delete_repo(id):
    repo = Repo.query.get(id)
    if repo:
        for event in repo.events:
            delete_event(event.id)
        db.session.delete(repo)
        db.session.commit()

def delete_platform(id, user_id):
    platform = UserPlatform.query.filter_by(id=id, user_id=user_id).first()
    if platform:
        for repo in platform.repos:
            delete_repo(repo.id)
        db.session.delete(platform)
        db.session.commit()

def delete_user(id):
    user = User.query.get(id)
    if user:
        for platform in user.platforms:
            delete_platform(platform.id, user.id)
        db.session.delete(user)
        db.session.commit()