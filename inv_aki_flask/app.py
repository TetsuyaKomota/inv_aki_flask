from flask import Flask

from inv_aki_flask.views import index


def launch():
    app = Flask(__name__)
    app.register_blueprint(index.view)
    return app


def launch_for_local():
    app = launch()
    app.run(port=8000, debug=True)


if __name__ == "__main__":
    launch()
