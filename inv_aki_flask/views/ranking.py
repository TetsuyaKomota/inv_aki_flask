from flask import Blueprint, render_template

from inv_aki_flask.model.datastore_client import client as datastore_client

view = Blueprint("ranking", __name__, url_prefix="/ranking")


@view.route("/", methods=["GET"])
def show():
    session_infos = datastore_client.get_public_sessions()

    # 順位とのtuple にして template に渡す
    session_infos = [(i+1, s) for i, s in enumerate(session_infos)]

    return render_template("ranking.html", session_infos=session_infos)
