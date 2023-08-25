from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.datastore_client.message import client as message_entity_client
from inv_aki_flask.model.datastore_client.report import client as report_entity_client
from inv_aki_flask.model.datastore_client.session import client as session_entity_client

view = Blueprint("result", __name__, url_prefix="/result")


@view.route("/<string:sessionid>", methods=["GET"])
def show(sessionid):
    session_info = session_entity_client.get_session(sessionid=sessionid)
    messages = message_entity_client.get_messages(sessionid=sessionid)

    judged = session.get("judged", False)

    thank = session.get("thank", "")

    if "thank" in session:
        del session["thank"]

    return render_template(
        "result.html",
        sessionid=sessionid,
        session_info=session_info,
        messages=messages,
        judged=judged,
        thank=thank,
    )


@view.route("/", methods=["POST"])
def post():
    sessionid = session.get("sessionid", "")
    name = session.get("name", "")
    session_info = session_entity_client.get_session(sessionid=sessionid)
    if session_info.get("judge", False):
        session_entity_client.update_session_entity(
            sessionid=sessionid,
            public=True,
            name=name,
            judge=False,  # 閲覧ページから再登録できないように
            expire_at=30,  # 記録したデータは30日間有効(FIXME 要調整)
        )
        messages = message_entity_client.get_messages(sessionid=sessionid)
        for message in messages:
            message_entity_client.update_message_expiration(
                message,
                expire_at=30,  # 記録したデータは30日間有効(FIXME 要調整)
            )

    return redirect(url_for("ranking.show"))


@view.route("/report", methods=["POST"])
def report():
    session["thank"] = "報告ありがとうございます"
    sessionid = request.form.get("sessionid", "")
    messageid = request.form.get("messageid", "")
    keyword = request.form.get("keyword", "")
    question = request.form.get("question", "")
    answer = request.form.get("answer", "")
    correct = request.form.get("correct", "")

    report_entity_client.create_report_entity(
        sessionid=sessionid,
        messageid=messageid,
        keyword=keyword,
        question=question,
        answer=answer,
        correct=correct,
    )

    return redirect(url_for("result.show", sessionid=sessionid))
