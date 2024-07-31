
from flask import make_response
from flask import jsonify as JSON


def jsonify(content, status=200):
    return make_response(JSON(content), status)
