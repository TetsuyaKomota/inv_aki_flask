from flask import Blueprint, render_template

from inv_aki_flask.model.datastore_client import client as datastore_client

view = Blueprint("ranking", __name__, url_prefix="/ranking")


@view.route("/", methods=["GET"])
def show():
    return render_template("ranking.html")
