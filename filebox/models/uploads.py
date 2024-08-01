"""FileBox database models"""

import json
import mongoengine as db

from datetime import datetime
from flask import url_for

from filebox.enums import BlobTypes


class FileBlob(db.Document):
    """ File entity """
    name = db.StringField()
    uri = db.FileField(required=True)
    size = db.IntField(max_value=10000000)  # TODO: Read from app config
    type = db.EnumField(BlobTypes, required=True, choices=[BlobTypes.JPG, BlobTypes.PNG, BlobTypes.PDF])

    meta = { 'strict': True, 'collection': 'blobs' }

    @property
    def database(self):
        return db.get_db()

    def to_json(self, *args, **kwargs):
        return json.dumps(dict(id=str(self.id), name=self.name, size=self.size, type=self.type.value))


class FileUpload(db.Document):
    """ File upload entity """
    hidden = db.BooleanField(default=False)
    timestamp = db.DateTimeField(default=datetime.now())
    blob = db.ReferenceField(FileBlob, required=True, reverse_delete_rule=db.CASCADE)

    meta = { 'strict': True, 'collection': 'uploads' }

    @classmethod
    def post_delete(cls, sender, document):
        try:
            FileBlob.objects(id=document.blob.id).delete()
        except FileBlob.DoesNotExist:
            pass

    def clean(self):
        try:
            assert FileBlob.objects.get(id=self.blob.id)
        except Exception as e:
            raise db.ValidationError("ReferenceField value<%s> does not exist" % self.blob)
        return super().clean()

    def to_json(self, *args, **kwargs):
        d = dict(
            id=str(self.id),
            hidden=self.hidden,
            timestamp=self.timestamp.ctime(),
            blob=json.loads(self.blob.to_json())
        )
        d.get('blob').update({'uri': url_for('blobs.show', id=str(self.id))})
        return json.dumps(d)


db.signals.post_delete.connect(FileUpload.post_delete, sender=FileUpload)
