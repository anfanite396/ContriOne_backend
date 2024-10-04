from flask import Blueprint

services_bp = Blueprint("services_bp", __name__)

@services_bp.route("/")
def home():
    return "Hello World"
