from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.datastore_client.message import client as message_entity_client
from inv_aki_flask.model.datastore_client.report import client as report_entity_client
from inv_aki_flask.model.datastore_client.session import client as session_entity_client
from inv_aki_flask.model.inner_session import (
    get_message_count,
    get_messages,
    get_name,
    get_sessionid,
    is_judged_in_session,
    pop_thank,
    set_thank,
)

view = Blueprint("result", __name__, url_prefix="/result")


@view.route("/<string:sessionid>", methods=["GET"])
def show(sessionid):
    session_info = session_entity_client.get_session(sessionid=sessionid)
    messages = message_entity_client.get_messages(sessionid=sessionid)

    is_same_session = sessionid == get_sessionid(session)

    thank = pop_thank(session)

    if get_message_count(session) > 0:
        dialog = get_messages(session)
        judge_comment = dialog.get_latest_system_response()
    else:
        judge_comment = ""

    return render_template(
        "result.html",
        sessionid=sessionid,
        session_info=session_info,
        messages=messages,
        judge_comment=judge_comment,
        is_same_session=is_same_session,
        thank=thank,
    )


@view.route("/", methods=["POST"])
def post():
    sessionid = get_sessionid(session)
    name = get_name(session)
    session_info = session_entity_client.get_session(sessionid=sessionid)
    if is_judged_in_session(session):
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
    set_thank(session, "報告ありがとうございます")
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
