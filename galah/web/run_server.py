DEBUG = True
SECRET_KEY = "development key"


def main():
    import mongoengine
    mongoengine.connect("galah")

    from galah.web import app

    app.config.from_object(__name__)
    app.run()

if __name__ == "__main__":
    main()
