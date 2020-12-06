import logging
import flask

from flask import Flask
from flask_restful import Resource, Api
from flask_restful.reqparse import RequestParser

from app.manager import get_aggregate_repo_data

app = Flask("user_profiles_api")
api = Api(app, prefix="/api/v1")

logger = flask.logging.create_logger(app)
logger.setLevel(logging.INFO)


class GetRepoAggregation(Resource):
    """
    The aggregation endpoint class lives here. 
    Usage: 
        POST with json body
        :param username: a string for the username on github and bitbucket
        :type username: str
    """

    def __init__(self):
        self.username_parser = RequestParser(bundle_errors=True)
        self.username_parser.add_argument("username", type=str, required=True, help="Username is required and must be a string")

    def post(self):
        try:
            args = self.username_parser.parse_args()
            resp = get_aggregate_repo_data(args['username'])
            return {"arg-data": resp}
        except Exception as e:
            # todo make better error handling for different errors 
            return {'error': 'there was an error processing your request'}

api.add_resource(GetRepoAggregation, '/aggregate')