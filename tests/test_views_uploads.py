
import json
import mimetypes
import unittest
import mongoengine as db
import mongomock as MockDB

from bson import ObjectId
from io import BytesIO
from os import path
from mongomock.gridfs import enable_gridfs_integration

from . import Env, fixtures
from filebox import app
from filebox.urls import Routes
from filebox.models.uploads import FileBlob, FileUpload


Routes.setup()
enable_gridfs_integration()


class Fixtures:
    @staticmethod
    def blobs():
        for fx in [fixtures.get('test.png'), fixtures.get('test.pdf'), fixtures.get('test.jpg')]:
            mime = mimetypes.guess_type(fx)[0]
            blob = FileBlob(name=path.basename(fx), size=path.getsize(fx), type=mime)
            with open(fx, 'rb') as fd:
                blob.uri.put(fd, content_type=mime)
            blob.save()

    @staticmethod
    def uploads():
        for blob in FileBlob.objects.all():
            FileUpload(blob=blob.id).save()

    @staticmethod
    def add(hidden=False):
        # Pick a fixture
        f = fixtures.get('test.pdf')

        # Create a blob entry
        mime = mimetypes.guess_type(f)[0]
        blob = FileBlob(name='fixture', size=path.getsize(f), type=mime)
        with open(f, 'rb') as fd:
            blob.uri.put(fd, content_type=mime)
        blob.save()

        # Create an upload
        FileUpload(hidden=hidden, blob=blob.id).save()

    @staticmethod
    def seed():
        Fixtures.blobs()
        Fixtures.uploads()


class TestUploads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.env = Env.load(app.config)
        cls.app = app.test_client()

    def setUp(self):
        self.url = self.env.host
        self.conn = db.connect(
            'testdb',
            host=app.config.get('MONGODB_HOST'),
            mongo_client_class=MockDB.MongoClient
        )
        Fixtures.seed()

    def test_fetch_uploads(self):
        r = self.app.get(self.url + '/uploads')

        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(json.loads(r.json)), 3)

    def test_hidden_uploads(self):
        Fixtures.add(hidden=True)

        r = self.app.get(self.url + '/uploads')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(json.loads(r.json)), 3)

        r = self.app.get(self.url + '/uploads?all=false')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(json.loads(r.json)), 3)

        r = self.app.get(self.url + '/uploads?all=true')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(json.loads(r.json)), 4)

        r = self.app.get(self.url + '/uploads?hidden=false')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(json.loads(r.json)), 3)

        r = self.app.get(self.url + '/uploads?hidden=true')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(json.loads(r.json)), 4)

    def test_create_upload(self):
        with open(fixtures.get('test.mp4'), 'rb') as fd:
            r = self.app.post(self.url + '/uploads',
                              data={'file': (BytesIO(fd.read()), 'test.pkpass')},
                              content_type='multipart/form-data')
            self.assertEqual(r.status_code, 413)

        with open(fixtures.get('test.pkpass'), 'rb') as fd:
            r = self.app.post(self.url + '/uploads',
                              data={'file': (BytesIO(fd.read()), 'test.pkpass')},
                              content_type='multipart/form-data')
            self.assertEqual(r.status_code, 415)

        with open(fixtures.get('test.pkpass'), 'rb') as fd:
            r = self.app.post(self.url + '/uploads',
                              data={'file': (BytesIO(fd.read()), 'test.pdf')},
                              content_type='multipart/form-data')
            self.assertEqual(r.status_code, 415)

        with open(fixtures.get('test.png'), 'rb') as fd:
            r = self.app.post(self.url + '/uploads',
                              data={'file': (BytesIO(fd.read()), 'test.png')},
                              content_type='multipart/form-data')
            item = json.loads(r.json)

            self.assertEqual(r.status_code, 200)
            self.assertFalse(item.get('hidden'))
            self.assertTrue('blob' in item.keys())

            self.assertGreater(FileBlob.objects.count(), 3)
            self.assertIsNotNone(FileBlob.objects.get(id=item.get('blob').get('$oid')))

            self.assertGreater(FileUpload.objects.count(), 3)
            self.assertIsNotNone(FileUpload.objects.get(id=item.get('_id').get('$oid')))

    def test_bulk_delete_uploads(self):
        """TODO: Add tests"""

    def tearDown(self) -> None:
        self.db = db.get_db()
        self.db.drop_collection('blobs')
        self.db.drop_collection('uploads')
        self.conn.drop_database(self.db.name)


class TestUploadItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.env = Env.load(app.config)
        cls.app = app.test_client()

    def setUp(self):
        self.url = self.env.host
        self.conn = db.connect(
            'testdb',
            host=app.config.get('MONGODB_HOST'),
            mongo_client_class=MockDB.MongoClient
        )
        Fixtures.seed()

    def test_get_upload_item(self):
        ex = FileUpload.objects.first()
        r = self.app.get(self.url + '/upload/foobar')
        self.assertEqual(r.status_code, 400)

        r = self.app.get(self.url + '/upload/%s' % ObjectId())
        self.assertEqual(r.status_code, 404)

        r = self.app.get(self.url + '/upload/%s' % str(ex.id))
        item = json.loads(r.json)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(item.get('_id').get('$oid'), str(ex.id))

        Fixtures.add(hidden=True)
        ex = FileUpload.objects.get(hidden=True)
        r = self.app.get(self.url + '/upload/%s' % str(ex.id))
        item = json.loads(r.json)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(item.get('_id').get('$oid'), str(ex.id))
        self.assertTrue(item.get('hidden'))

    def test_put_upload_item(self):
        ex = FileUpload.objects.first()
        r = self.app.put(self.url + '/upload/foobar', json={'size': 2048})
        self.assertEqual(r.status_code, 400)

        r = self.app.put(self.url + '/upload/%s' % ObjectId(), json={'hidden': True})
        self.assertEqual(r.status_code, 404)

        r = self.app.put(self.url + '/upload/%s' % str(ex.id), json={'hidden': True})
        item = json.loads(r.json)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(item.get('hidden'))
        self.assertEqual(item.get('_id').get('$oid'), str(ex.id))

        r = self.app.put(self.url + '/upload/%s' % str(ex.id), json={'hidden': False})
        item = json.loads(r.json)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(item.get('hidden'))
        self.assertEqual(item.get('_id').get('$oid'), str(ex.id))

    def test_delete_upload_item(self):
        r = self.app.delete(self.url + '/upload/foobar')
        self.assertEqual(r.status_code, 400)

        r = self.app.delete(self.url + '/upload/%s' % ObjectId())
        self.assertEqual(r.status_code, 404)

        ex = FileUpload.objects.first()
        r = self.app.delete(self.url + '/upload/%s' % str(ex.id))
        self.assertEqual(r.json.get('deleted'), str(ex.id))
        with self.assertRaises(db.DoesNotExist):
            FileUpload.objects.get(id=ex.id)

        r = self.app.delete(self.url + '/upload/%s' % str(ex.id))
        self.assertEqual(r.status_code, 404)

    def tearDown(self) -> None:
        self.db = db.get_db()
        self.db.drop_collection('blobs')
        self.db.drop_collection('uploads')
        self.conn.drop_database(self.db.name)