
from flask import Flask


app = Flask('filebox')
app.config.from_object('filebox.config')
app.config.from_pyfile('config.py', silent=True)
