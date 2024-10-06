from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource

health_bp = Blueprint("health_bp", __name__)
api = Api(health_bp)


class Health(Resource):
    def options(self):
        return make_response(jsonify({"message" : "Success"}), 200)
    def get(self):
        return make_response(jsonify({"message" : "Success"}), 200)

api.add_resource(Health, "/")
