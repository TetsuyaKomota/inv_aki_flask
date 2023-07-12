from flask import Flask

from inv_aki_flask.views import index

app = Flask(__name__)
app.register_blueprint(index.view)

def launch_for_local():
    app.run(port=8000, debug=True)

