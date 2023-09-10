import os

from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.chatgpt import MAX_QUESTIONS, ChatGPT
from inv_aki_flask.model.datastore_client.message import client as message_entity_client
from inv_aki_flask.model.datastore_client.session import client as session_entity_client
from inv_aki_flask.model.inner_session import (
    get_keyword,
    get_message_count,
    get_messageid,
    get_messages,
    get_name,
    get_notice,
    get_sessionid,
    had_init_session,
    had_view_ad_in_session,
    init_session,
    is_judged_in_session,
    is_login,
    judged_in_session,
    pop_sessionid,
    set_message,
    set_notice,
    view_ad_in_session,
)

view = Blueprint("main", __name__, url_prefix="/main")


if os.path.exists("tmp/api_key.txt"):
    with open("tmp/api_key.txt", "r") as f:
        api_key = f.read().strip()
    model = ChatGPT(api_key)
else:
    model = ChatGPT()


def put_session_entity(sessionid: str, category: str, keyword: str) -> None:
    session_entity_client.create_session_entity(
        sessionid, category=category, keyword=keyword
    )


def put_message_entity(res: dict[str, str], sessionid: str, messageid: str) -> None:
    message_entity_client.create_message_entity(
        sessionid=sessionid,
        messageid=messageid,
        question=res.get("question", ""),
        answer=res.get("answer", ""),
        reason1=res.get("reason1", ""),
        reason2=res.get("reason2", ""),
        reason3=res.get("reason3", ""),
    )


@view.route("/", methods=["GET"])
def show():
    if not is_login(session):
        return redirect(url_for("login.show"))

    if not had_init_session(session):
        category, keyword = model.select_keyword()
        sessionid = init_session(session, category, keyword)
        put_session_entity(sessionid, category=category, keyword=keyword)

    message_data = get_messages(session)
    ans_count = get_message_count(session)

    if ans_count == 0:
        input_text = "漫画やアニメに登場する？"
    else:
        input_text = ""

    judged = is_judged_in_session(session)

    notice = get_notice(session)

    viewad = had_view_ad_in_session(session)

    if viewad:
        max_count = MAX_QUESTIONS * 3
        ad_disabled = "disabled"
    else:
        max_count = MAX_QUESTIONS
        ad_disabled = ""

    return render_template(
        "main.html",
        title="逆アキネイター",
        name=get_name(session),
        data=message_data,
        ans_count=ans_count,
        max_count=max_count,
        ad_disabled=ad_disabled,
        judged=judged,
        input_text=input_text,
        notice=notice,
    )


@view.route("/", methods=["POST"])
def post():
    if not is_login(session):
        return redirect(url_for("login.show"))

    msg = request.form.get("comment")
    typ = request.form.get("action")

    sessionid = get_sessionid(session)

    if typ == "答え合わせする":
        return redirect(url_for("result.show", sessionid=sessionid))

    if typ == "広告を視聴して質問回数を増やす":
        view_ad_in_session(session)
        return redirect(url_for("main.show"))

    if typ == "リセット":
        pop_sessionid(session)
        return redirect(url_for("main.show"))

    # comment が空の場合は警告出す
    if not msg:
        if typ == "質問する":
            target = "質問"
        elif typ == "回答する":
            target = "キーワード"
        set_notice(session, f"{target}を入力してください")
        return redirect(url_for("main.show"))
    else:
        set_notice(session, "")

    messageid = get_messageid(session)
    category, keyword = get_keyword(session)

    if typ == "質問する":
        ans, res = model.ask_answer(msg, category, keyword)
        put_message_entity(res, sessionid, messageid)

    elif typ == "回答する":
        judged_in_session(session)
        ans, res = model.judge(msg, category, keyword)

        answer = msg
        ans_count = get_message_count(session)
        explain1 = res.get("explain1", None)
        explain2 = res.get("explain2", None)
        reason = res.get("reason", None)
        judge = ans.startswith("正解！")

        session_entity_client.update_session_entity(
            sessionid=sessionid,
            count=ans_count,
            answer=answer,
            explain1=explain1,
            explain2=explain2,
            reason=reason,
            judge=judge,
        )

    set_message(session, msg, ans)

    return redirect(url_for("main.show"))
