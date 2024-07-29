""" Filebox API """

from flask import Flask
from flask import request, redirect, url_for


app = Flask('filebox', instance_relative_config=True)
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
    showHidden = request.args.get('hidden', False)


@app.route('/upload/<uid>', methods=['GET', 'PUT'])
def upload(uid):
    """
    Fetch details for a specific file upload.
    """


@app.route('uploads/delete', methods=['DELETE'])
def clear():
    """
    Delete multiple uploaded files.
    """
