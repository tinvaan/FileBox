
from flask import Flask
from flask import redirect, url_for


app = Flask('filebox')
app.config.from_object('filebox.config')
app.config.from_pyfile('config.py', silent=True)

@app.route('/')
def home():
    return redirect(url_for('uploads.items'))
