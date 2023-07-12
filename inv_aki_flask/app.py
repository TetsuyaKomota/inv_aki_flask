from flask import Flask

from inv_aki_flask.views import index, main

app = Flask(__name__)
app.register_blueprint(index.view)
app.register_blueprint(main.view)
app.secret_key = b"random string..."


def launch_for_local():
    app.run(port=8000, debug=True)
