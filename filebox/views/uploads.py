""" Filebox upload endpoints """

from mongoengine.errors import FieldDoesNotExist, ValidationError
from flask import Blueprint
from flask.views import MethodView
from flask import jsonify, make_response, request

from filebox.models import FileUpload


uploads = Blueprint('uploads', __name__)


class Uploads(MethodView):
    def get(self):
        return FileUpload.objects(hidden=request.args.get('hidden', False)).to_json()

    def delete(self):
        targets = request.get_json('files', [])
        removed = FileUpload.objects(blob__in=targets).delete()
        return jsonify({'deleted': removed})


class UploadItem(MethodView):
    def get(self, id):
        try:
            return FileUpload.objects.get(uid=id).to_json()
        except FileUpload.DoesNotExist:
            return make_response(jsonify({'error': 'Upload(%s) not found' % id}), 404)

    def put(self, id):
        try:
            f = FileUpload.objects.get(uid=id)
            f.update(**request.get_json())
            f.save()
            return f.to_json()
        except FileUpload.DoesNotExist:
            return make_response(jsonify({'error': 'Upload(%s) not found' % id}), 404)
        except (FieldDoesNotExist, ValidationError):
            return make_response(jsonify({'error': 'Failed to update upload(%s)' % id}), 400)

    def delete(self, id):
        try:
            f = FileUpload.objects.get(uid=id)
            f.delete()
            return jsonify({'deleted': f.uid})
        except FileUpload.DoesNotExist:
            return make_response(jsonify({'error': 'Upload(%s) not found' % id}), 404)
