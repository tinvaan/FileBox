""" FileBox server """

import mongoengine as db
import mongomock as MockDB

from mongomock.gridfs import enable_gridfs_integration

from filebox.views import app


enable_gridfs_integration()
db.connect(
    app.config.get('MONGODB_DB'),
    host=app.config.get('MONGODB_HOST'),
    mongo_client_class=MockDB.MongoClient
)

from filebox.urls import Routes
Routes.setup()

app.run(
    debug=True,
    port=app.config.get('FILEBOX_PORT'),
    host=app.config.get('FILEBOX_SERVER')
)
