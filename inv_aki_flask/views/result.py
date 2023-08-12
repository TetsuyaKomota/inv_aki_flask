from flask import Blueprint, render_template, session

from inv_aki_flask.model.datastore_client import client as datastore_client

view = Blueprint("result", __name__, url_prefix="/result")


@view.route("/", methods=["GET"])
def show():
    if not session.get("login", False):
        return redirect(url_for("login.show"))

    sessionid = session.get("sessionid", "")
    messages = datastore_client.get_messages(sessionid=sessionid)
    return render_template("result.html", messages=messages)
