
from filebox.views import app
from filebox.views.uploads import uploads, Uploads, UploadItem


class Routes:
    @staticmethod
    def rules():
        uploads.add_url_rule('/uploads', view_func=Uploads.as_view('uploads'))
        uploads.add_url_rule('/uploads/<id>', view_func=UploadItem.as_view('upload'))

    @staticmethod
    def register():
        app.register_blueprint(uploads)

    @staticmethod
    def setup():
        Routes.rules()
        Routes.register()
