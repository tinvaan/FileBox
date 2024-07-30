"""FileBox database models"""

from datetime import datetime
from enum import Enum

import mongoengine as db


class Types(Enum):
    """ Supported file types """
    PNG = 'image/png'
    JPG = 'image/jpeg'
    PDF = 'application/pdf'


class FileBlob(db.Document):
    """ File entity """
    uid = db.UUIDField()
    name = db.StringField()
    size = db.IntField(max_value=10000000)  # TODO: Read from app config
    hidden = db.BooleanField(default=False)
    type = db.EnumField(Types, choices=[Types.JPG, Types.PNG, Types.PDF])
    uri = db.FileField(unique=True, choices=[Types.JPG, Types.PNG, Types.PDF])

    meta = { 'collection': 'blobs' }

    @property
    def created_at(self):
        """ Return when a file was first uploaded """
        # TODO: Implement logic


class FileUpload(db.Document):
    """ File upload meta entity """
    uid = db.UUIDField()
    timestamp = db.DateTimeField(default=datetime.now())
    blob = db.ReferenceField(FileBlob, required=True, reverse_delete_rule=db.CASCADE)

    meta = { 'collection': 'uploads' }
