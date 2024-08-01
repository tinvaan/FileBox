
from gridfs import GridFS
from mongoengine.errors import FieldDoesNotExist
from flask import send_file
from flask import Blueprint
from flask.views import MethodView

from filebox.models import FileBlob, FileUpload
from filebox.utils import jsonify


blobs = Blueprint('blobs', __name__)


class BlobsView(MethodView):
    def get(self, id):
        try:
            upload = FileUpload.objects.get(id=id)
            blob = FileBlob.objects.get(id=upload.blob.id)

            fs = GridFS(blob.database)
            file = fs.get(blob.uri.grid_id)
            return send_file(file, as_attachment=False, mimetype=blob.type.value)
        except FieldDoesNotExist:
            return jsonify({'error': 'Unable to fetch file(%s)' % str(id)}, 400)
        except (FileBlob.DoesNotExist, FileUpload.DoesNotExist):
            return jsonify({'error': 'File(%s) not found' % str(id)}, 404)
