
from filebox.views import app
from filebox.views.uploads import uploads, Uploads, UploadItem


class Routes:
    @classmethod
    def setup(cls):
        cls().rules.register()

    @property
    def rules(self):
        uploads.add_url_rule('/uploads', view_func=Uploads.as_view('uploads'))
        uploads.add_url_rule('/uploads/<id>', view_func=UploadItem.as_view('upload'))
        return self

    @staticmethod
    def register():
        app.register_blueprint(uploads)
