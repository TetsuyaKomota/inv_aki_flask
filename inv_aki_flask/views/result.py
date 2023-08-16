from flask import Blueprint, redirect, render_template, session, url_for

from inv_aki_flask.model.datastore_client.message import client as message_entity_client
from inv_aki_flask.model.datastore_client.session import client as session_entity_client

view = Blueprint("result", __name__, url_prefix="/result")


@view.route("/<string:sessionid>", methods=["GET"])
def show(sessionid):
    session_info = session_entity_client.get_session(sessionid=sessionid)
    messages = message_entity_client.get_messages(sessionid=sessionid)
    return render_template("result.html", session_info=session_info, messages=messages)


@view.route("/", methods=["POST"])
def post():
    sessionid = session.get("sessionid", "")
    session_info = session_entity_client.get_session(sessionid=sessionid)
    if session_info.get("judge", False):
        session_entity_client.update_session_entity(
            sessionid=sessionid,
            public=True,
            judge=False,  # 閲覧ページから再登録できないように
            expire_at=7,  # 記録したデータは7日間有効(FIXME 要調整)
        )
        messages = message_entity_client.get_messages(sessionid=sessionid)
        for message in messages:
            message_entity_client.update_message_expiration(
                message,
                expire_at=7,  # 記録したデータは7日間有効(FIXME 要調整)
            )

    return redirect(url_for("ranking.show"))
