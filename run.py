""" FileBox server """

from filebox.api import app


app.run(
    debug=True,
    port=app.config.get('FILEBOX_PORT'),
    host=app.config.get('FILEBOX_SERVER')
)
