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
        return jsonify(FileUpload.objects.filter(**kwargs).to_json())

    def post(self):
        try:
            file = request.files.get('file')
            if not file:
                raise ValidationError('Incorrect file specification')

            supported = [choice.value for choice in FileBlob.type.choices]
            if file.mimetype in supported:
                mime = Magic(mime=True)
                content = copy(file.stream)
                actual = mime.from_buffer(content.read())

                if actual in supported:
                    kwargs = {
                        'type': actual,
                        'size': content.tell(),
                        'name': secure_filename(file.filename),
                    }
                    blob = FileBlob(**kwargs)
                    blob.uri.put(content, content_type=actual)
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
            item = json.loads(FileUpload.objects.get(id=id).to_json())
            item.update({
                'blob': url_for('blobs.show', id=str(item.get('_id').get('$oid')))
            })
            return jsonify(item)
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
