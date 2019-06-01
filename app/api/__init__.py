from flask import Blueprint

from flask_restful import Api

bp = Blueprint('api', __name__)
api = Api(bp)

from . import tasks
