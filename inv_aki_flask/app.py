from datetime import datetime
from hashlib import md5

from flask import Flask

from inv_aki_flask.views import index, login, main, result

app = Flask(__name__, static_folder="./static/")
app.register_blueprint(index.view)
app.register_blueprint(main.view)
app.register_blueprint(login.view)
app.register_blueprint(result.view)
app.secret_key = md5(str(datetime.now()).encode("utf-8")).hexdigest()


def launch_for_local():
    app.run(port=8000, debug=True)
