from config import view

class Home:
    def GET(self):
        return view.home()
