
import unittest
import mimetypes
import mongoengine as db
import mongomock as MockDB

from bson import ObjectId
from copy import deepcopy
from os import path
from mongomock.gridfs import enable_gridfs_integration

from . import fixtures
from filebox import app
from filebox.enums import BlobTypes
from filebox.models.uploads import FileBlob, FileUpload


class TestFileBlob(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        enable_gridfs_integration()

    def setUp(self):
        self.conn = db.connect(
            'testdb',
            host=app.config.get('MONGODB_HOST'),
            mongo_client_class=MockDB.MongoClient
        )

    def test_create_unsupported_blobs(self):
        for blob in [
            FileBlob(name='zero', size=0),
            FileBlob(name='one', size=10, type='text/plain'),
            FileBlob(name='two', size=20, type='video/mp4'),
            FileBlob(name='three', size=30, type='text/doc'),
            FileBlob(name='large', size=pow(10, 10), type='application/pdf')
        ]:
            with self.assertRaises(db.ValidationError):
                blob.save()

    def test_create_file_blob_with_minimum_fields(self):
        fb = FileBlob(name='minimal', size=100, type='application/pdf').save()

        self.assertIsNotNone(fb.id)
        self.assertEqual(fb.size, 100)
        self.assertEqual(fb.name, 'minimal')
        self.assertEqual(fb.type.value, 'application/pdf')

    def test_file_blob_update(self):
        fb = FileBlob(name='update_test', size=200, type='application/pdf').save()
        fb.size = 300
        fb.save()

        f = FileBlob.objects(id=fb.id).first()
        self.assertEqual(f.size, 300)

    def test_file_blob_delete(self):
        tag = ObjectId()
        fb = FileBlob(id=tag, name='to_delete', size=50, type='image/png').save()
        fb.delete()

        self.assertEqual(FileBlob.objects.filter(id=tag).count(), 0)

    def test_file_blob_with_all_fields(self):
        fb = FileBlob(name='complete', size=1000, type='image/jpeg')
        fb.save()
        retrieved_blob = FileBlob.objects(id=fb.id).first()
        self.assertEqual(retrieved_blob.name, 'complete')
        self.assertEqual(retrieved_blob.size, 1000)
        self.assertEqual(retrieved_blob.type.value, 'image/jpeg')

    def tearDown(self):
        self.db = db.get_db()
        self.db.drop_collection('blobs')
        self.conn.drop_database(self.db.name)


class TestFileUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        enable_gridfs_integration()

    def setUp(self):
        self.conn = db.connect(
            'testdb',
            host=app.config.get('MONGODB_HOST'),
            mongo_client_class=MockDB.MongoClient
        )

    def blob(self, name, save=False):
        fx = fixtures.get(name)
        blob = FileBlob(name=name, size=path.getsize(fx), type=BlobTypes.JPG)
        with open(fx, 'rb') as fd:
            blob.uri.put(fd, content_type=mimetypes.guess_type(fx))
        return blob if not save else blob.save()

    def test_create_file_upload_invalid_params(self):
        with self.assertRaises(db.FieldDoesNotExist):
            FileUpload(name='test.txt', size=1024, type='text/plain').save()

    def test_create_file_upload(self):
        blob = self.blob('test.pdf', save=True)
        upload = FileUpload(blob=blob.id).save()

        self.assertIsNotNone(upload.id)
        self.assertIsNotNone(upload.timestamp)

    def test_edit_file_upload(self):
        blob = self.blob('test.png', save=True)
        upload = FileUpload(blob=blob.id).save()
        before = deepcopy(upload)
        upload.save()

        self.assertNotEqual(before.state, upload.state)

    def test_delete_file_upload(self):
        blob = self.blob('test.jpg', save=True)
        upload = FileUpload(blob=blob.id).save()
        upload.delete()

        with self.assertRaises(db.DoesNotExist):
            FileBlob.objects.get(id=blob.id)

        with self.assertRaises(db.DoesNotExist):
            FileUpload.objects.get(id=upload.id)

    def tearDown(self):
        self.db = db.get_db()
        self.db.drop_collection('uploads')
        self.conn.drop_database(self.db.name)
