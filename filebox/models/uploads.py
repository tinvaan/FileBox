"""FileBox database models"""

import datetime as dt
import mongoengine as db

from filebox.enums import BlobTypes, FileState


class FileBlob(db.Document):
    """ File entity """
    name = db.StringField()
    uri = db.FileField(required=True)
    size = db.IntField(max_value=10000000)  # TODO: Read from app config
    hidden = db.BooleanField(default=False)
    type = db.EnumField(BlobTypes, required=True, choices=[BlobTypes.JPG, BlobTypes.PNG, BlobTypes.PDF])

    meta = { 'strict': True, 'collection': 'blobs' }


class FileUpload(db.Document):
    """ File upload entity """
    timestamp = db.DateTimeField(default=dt.datetime.now())
    state = db.EnumField(FileState, default=FileState.OK)
    blob = db.ReferenceField(FileBlob, required=True, reverse_delete_rule=db.CASCADE)

    meta = { 'strict': True, 'collection': 'uploads' }

    def clean(self):
        try:
            assert FileBlob.objects.get(id=self.blob.id)
        except Exception as e:
            raise db.ValidationError("ReferenceField value<%s> does not exist" % self.blob)
        return super().clean()
