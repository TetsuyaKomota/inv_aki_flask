import os
from datetime import datetime
from hashlib import md5

from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.chatgpt import MAX_QUESTIONS, ChatGPT
from inv_aki_flask.model.datastore_client import client as datastore_client

view = Blueprint("main", __name__, url_prefix="/main")

if os.path.exists("tmp/api_key.txt"):
    with open("tmp/api_key.txt", "r") as f:
        api_key = f.read().strip()
    model = ChatGPT(api_key, "")
else:
    model = ChatGPT()


def generate_sessionid(id):
    text = f"{id}_{datetime.now()}"
    return md5(text.encode("utf-8")).hexdigest()


def put_session(sessionid):
    datastore_client.create_session_entity(sessionid)


def put_message(work, keyword, res, sessionid, messageid):
    datastore_client.create_message_entity(
        sessionid=sessionid,
        messageid=messageid,
        work=work,
        keyword=keyword,
        question=res.get("question", ""),
        answer=res.get("answer", ""),
        reason1=res.get("reason1", ""),
        reason2=res.get("reason2", ""),
        reason3=res.get("reason3", ""),
    )


def init_message(id):
    msg = "\n".join(
        [
            "有名な人物やキャラクターを思い浮かべて．",
            "魔人が誰でも当てて見せよう．",
        ]
    )

    ans = "よーし，やってみるぞー"

    message_data = [
        (
            (f"アキ{id}", msg),
            ("ChatGPT", ans),
            0,
        )
    ]

    return message_data


@view.route("/", methods=["GET"])
def show():
    if not session.get("login", False):
        return redirect(url_for("login.show"))

    if "messages" not in session:
        session["messages"] = init_message(session["id"])
        input_text = "男性キャラクター？"
    else:
        input_text = ""

    if "keyword" not in session:
        work, keyword = model.select_keyword()
        session["work"] = work
        session["keyword"] = keyword
        session["sessionid"] = generate_sessionid(session["id"])
        put_session(session["sessionid"])

    message_data = session["messages"]
    judged = "judged" in session

    msg = f"Login ID: {session['id']}"
    return render_template(
        "main.html",
        title="逆アキネイター",
        message=msg,
        data=message_data,
        ans_count=len(message_data) - 1,  # 最初のセリフ分
        max_count=MAX_QUESTIONS,
        judged=judged,
        input_text=input_text,
    )


@view.route("/", methods=["POST"])
def post():
    if not session.get("login", False):
        return redirect(url_for("login.show"))

    msg = request.form.get("comment")
    typ = request.form.get("action")

    if typ == "答え合わせ":
        return redirect(url_for("result.show"))

    if typ == "リセット":
        for k in ["messages", "work", "keyword", "judged"]:
            if k in session:
                del session[k]
        return redirect(url_for("main.show"))

    if "messages" not in session:
        session["messages"] = init_message(session["id"])

    message_data = session["messages"]

    work = session.get("work", "")
    keyword = session.get("keyword", "")
    sessionid = session.get("sessionid", "")
    messageid = len(message_data)

    if typ == "質問する":
        ans, res = model.ask_answer(msg, work, keyword)
        put_message(work, keyword, res, sessionid, messageid)

    elif typ == "回答する":
        ans, judge = model.judge(msg, work, keyword)
        session["judged"] = True
        datastore_client.update_session_entity(
            sessionid=sessionid, judge=judge, rank=messageid
        )

    message_data.append(
        (
            (f"アキ{session['id']}", msg),
            ("ChatGPT", ans),
            len(message_data),
        )
    )

    session["messages"] = message_data

    return redirect(url_for("main.show"))
