""" Filebox upload endpoints """

import json

from copy import copy
from magic import Magic
from mongoengine.errors import FieldDoesNotExist, OperationError, ValidationError
from flask import Blueprint
from flask.views import MethodView
from flask import request, url_for
from werkzeug.utils import secure_filename

from filebox.models import FileBlob, FileUpload
from filebox.utils import jsonify


uploads = Blueprint('uploads', __name__)


class Uploads(MethodView):
    def get(self):
        show_all = False if str(request.args.get('all', 'false')).lower() == 'false' else True
        show_hidden = False if str(request.args.get('hidden', 'false')).lower() == 'false' else True
        kwargs = {} if show_all or show_hidden else {'hidden': show_hidden}
        return jsonify([
            json.loads(doc.to_json()) for doc in FileUpload.objects.filter(**kwargs)
        ])

    def post(self):
        try:
            file = request.files.get('file')
            if not file:
                raise ValidationError('Incorrect file specification')

            supported = [choice.value for choice in FileBlob.type.choices]
            if file.mimetype in supported:
                mime = Magic(mime=True)
                contents = copy(file.stream.read())
                mimetype = mime.from_buffer(contents)

                if mimetype in supported:
                    kwargs = {
                        'type': mimetype,
                        'size': len(contents),
                        'name': secure_filename(file.filename),
                    }
                    blob = FileBlob(**kwargs)
                    blob.uri.put(contents, content_type=mimetype)
                    blob.save()

                    return jsonify(FileUpload(blob=blob).save().to_json())

            return jsonify({'error': 'File type not supported'}, 415)
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
            data = request.get_json()
            kwargs = {**({'hidden': data.get('hidden')} if 'hidden' in data.keys() else {})}
            file = FileUpload.objects.get(id=id)
            if not file.modify(**kwargs):
                return jsonify({'error': 'Unable to update "%s"' % id}, 500)
            return jsonify(file.save().to_json())
        except FileUpload.DoesNotExist:
            return jsonify({'error': 'Upload(%s) not found' % id}, 404)
        except (FieldDoesNotExist, ValidationError):
            return jsonify({'error': 'Failed to update upload(%s)' % id}, 400)

    def delete(self, id):
        try:
            file = FileUpload.objects.get(id=id)
            file.delete()
            return jsonify({'deleted': str(file.id)})
        except FileUpload.DoesNotExist:
            return jsonify({'error': 'Upload(%s) not found' % id}, 404)
        except ValidationError:
            return jsonify({'error': 'Failed to delete upload(%s)' % id}, 400)
