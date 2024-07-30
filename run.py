""" FileBox server """

import mongoengine as db
import mongomock as MockDB

from filebox.api import app


db.connect(
    app.config.get('MONGODB_DB'),
    host=app.config.get('MONGODB_HOST'),
    mongo_client_class=MockDB.MongoClient
)

app.run(
    debug=True,
    port=app.config.get('FILEBOX_PORT'),
    host=app.config.get('FILEBOX_SERVER')
)
