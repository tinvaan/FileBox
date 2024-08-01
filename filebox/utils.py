
import json

from flask import make_response
from flask import jsonify as JSON


def jsonify(content, status=200):
    try:
        content = json.loads(content)
    except Exception:
        pass

    return make_response(JSON(content), status)
