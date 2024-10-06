import os
from flask import Flask
from flask_cors import CORS
from flask_session import Session

from .api import api_bp
from .services import services_bp
from .health import health_bp
from .models.users import db

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_DOMAIN'] = None
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    MYSQL_USER = os.getenv('MYSQL_USER')
    print(MYSQL_USER)
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    SECRET_KEY = os.getenv('SECRET_KEY')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)

    app.register_blueprint(services_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(health_bp, url_prefix="/health")
    
    return app
