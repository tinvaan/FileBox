
from filebox.views import app
from filebox.views.blobs import blobs, BlobsView
from filebox.views.uploads import uploads, Uploads, UploadItem


class Routes:
    @classmethod
    def setup(cls):
        cls().rules.register()

    @property
    def rules(self):
        uploads.add_url_rule('/uploads', view_func=Uploads.as_view('items'))
        uploads.add_url_rule('/upload/<id>', view_func=UploadItem.as_view('item'))
        blobs.add_url_rule('/upload/<id>/blobs', view_func=BlobsView.as_view('show'))
        return self

    @staticmethod
    def register():
        app.register_blueprint(uploads)
        app.register_blueprint(blobs)
