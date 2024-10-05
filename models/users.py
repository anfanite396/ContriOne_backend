from . import db

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