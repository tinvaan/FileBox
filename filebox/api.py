""" Filebox API """

from flask import Flask
from flask import jsonify, redirect, request, url_for

from .models import Upload


app = Flask('filebox')
app.config.from_object('filebox.config')
app.config.from_pyfile('config.py', silent=True)


@app.route('/')
def home():
    """
    API home page, redirects to /uploads.
    """
    return redirect(url_for('history'))


@app.route('/uploads')
def history():
    """
    View history of file uploads.
    """
    return Upload.objects(hidden=request.args.get('hidden', False)).to_json()


@app.route('/upload/<uid>', methods=['GET', 'PUT'])
def upload(uid):
    """
    Fetch details for a specific file upload.
    """
    return Upload.objects.get(uid=uid).to_json()


@app.route('/uploads/delete', methods=['DELETE'])
def clear():
    """
    Delete multiple uploaded files.
    """
    status = {'deleted': []}
    for file in request.get_json().get('files', []):
        u = Upload.objects(blob=file)
        u.delete()
        status['deleted'] = status.get('deleted', []) + [u.to_json()]
    return jsonify(status)
