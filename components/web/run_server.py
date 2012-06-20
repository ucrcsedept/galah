import mongoengine
mongoengine.connect("galah")

from galahweb import app

DEBUG = True
SECRET_KEY = "development key"

app.config.from_object(__name__)
app.run()
