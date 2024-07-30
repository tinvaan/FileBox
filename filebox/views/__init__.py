
from flask import Flask

from .uploads import uploads

app = Flask('filebox')
app.config.from_object('filebox.config')
app.config.from_pyfile('config.py', silent=True)

app.register_blueprint(uploads)