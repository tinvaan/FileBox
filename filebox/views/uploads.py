""" Filebox upload endpoints """

from mongoengine.errors import FieldDoesNotExist, OperationError, ValidationError
from flask import Blueprint
from flask.views import MethodView
from flask import request
from werkzeug.utils import secure_filename

from filebox.models import FileUpload
from filebox.utils import jsonify


uploads = Blueprint('uploads', __name__)


class Uploads(MethodView):
    def get(self):
        show_all = False if str(request.args.get('all', 'false')).lower() == 'false' else True
        show_hidden = False if str(request.args.get('hidden', 'false')).lower() == 'false' else True
        kwargs = {} if show_all or show_hidden else {'hidden': show_hidden}
        return jsonify(FileUpload.objects.filter(**kwargs).to_json())

    def post(self):
        try:
            file = request.files.get('file')
            params = request.get_json()
            params.update({
                'type': file.mimetype, 'name': secure_filename(file.filename)
            })
            return jsonify(FileUpload(**params).save().to_dict())
        except (FieldDoesNotExist, ValidationError):
            return jsonify({'error': 'Failed to upload file'}, 400)

    def delete(self):
        try:
            targets = request.get_json('files', [])
            removed = FileUpload.objects(blob__in=targets).delete()
            return jsonify({'deleted': removed})
        except OperationError:
            return jsonify({'error': 'Failed to delete some uploads'}, 500)


class UploadItem(MethodView):
    def get(self, id):
        try:
            return jsonify(FileUpload.objects.get(id=id).to_json())
        except FileUpload.DoesNotExist:
            return jsonify({'error': 'Upload(%s) not found' % id}, 404)
        except ValidationError:
            return jsonify({'error': 'Failed to retrieve upload(%s)' % id}, 400)

    def put(self, id):
        try:
            f = FileUpload.objects.get(uid=id)
            f.update(**request.get_json())
            return jsonify(f.save().to_json())
        except FileUpload.DoesNotExist:
            return jsonify({'error': 'Upload(%s) not found' % id}, 404)
        except (FieldDoesNotExist, ValidationError):
            return jsonify({'error': 'Failed to update upload(%s)' % id}, 400)

    def delete(self, id):
        try:
            f = FileUpload.objects.get(uid=id)
            f.delete()
            return jsonify({'deleted': f.uid})
        except FileUpload.DoesNotExist:
            return jsonify({'error': 'Upload(%s) not found' % id}, 404)
