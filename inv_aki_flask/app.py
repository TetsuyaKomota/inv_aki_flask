from datetime import datetime
from hashlib import md5

from flask import Flask

from inv_aki_flask.views import index, login, main, ranking, result

app = Flask(__name__, static_folder="./static/")
app.register_blueprint(index.view)
app.register_blueprint(main.view)
app.register_blueprint(login.view)
app.register_blueprint(result.view)
app.register_blueprint(ranking.view)
app.secret_key = md5(
    str(datetime.now()).encode("utf-8"), usedforsecurity=False
).hexdigest()


def launch_for_local(debug: bool = False) -> None:
    app.run(port=8000, debug=debug)


if __name__ == "__main__":
    launch_for_local(debug=True)
