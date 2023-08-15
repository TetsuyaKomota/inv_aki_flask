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


def generate_sessionid(name):
    text = f"{name}_{datetime.now()}"
    return md5(text.encode("utf-8")).hexdigest()


def put_session(sessionid, category, keyword):
    datastore_client.create_session_entity(
        sessionid, category=category, keyword=keyword
    )


def put_message(res, sessionid, messageid):
    datastore_client.create_message_entity(
        sessionid=sessionid,
        messageid=messageid,
        question=res.get("question", ""),
        answer=res.get("answer", ""),
        reason1=res.get("reason1", ""),
        reason2=res.get("reason2", ""),
        reason3=res.get("reason3", ""),
    )


def init_message(name):
    msg = "\n".join(
        [
            "有名な人物やキャラクターを思い浮かべて．",
            "魔人が誰でも当てて見せよう．",
        ]
    )

    ans = "よーし，やってみるぞー"

    message_data = [
        (
            (f"アキ{name}", msg),
            ("ChatGPT", ans),
            0,
        )
    ]

    return message_data


@view.route("/", methods=["GET"])
def show():
    if "login" not in session or "name" not in session:
        return redirect(url_for("login.show"))

    if "messages" not in session:
        session["messages"] = init_message(session["name"])
        input_text = "男性キャラクター？"
    else:
        input_text = ""

    if "keyword" not in session:
        category, keyword = model.select_keyword()
        session["category"] = category
        session["keyword"] = keyword
        session["sessionid"] = generate_sessionid(session["name"])
        put_session(session["sessionid"], category=category, keyword=keyword)

    message_data = session["messages"]
    judged = "judged" in session

    msg = f"Login ID: {session['name']}"
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
    if "login" not in session or "name" not in session:
        return redirect(url_for("login.show"))

    msg = request.form.get("comment")
    typ = request.form.get("action")

    sessionid = session.get("sessionid", "")

    if typ == "答え合わせ":
        return redirect(url_for("result.show", sessionid=sessionid))

    if typ == "リセット":
        for k in ["messages", "category", "keyword", "judged"]:
            if k in session:
                del session[k]
        return redirect(url_for("main.show"))

    if "messages" not in session:
        session["messages"] = init_message(session["name"])

    message_data = session["messages"]

    category = session.get("category", "")
    keyword = session.get("keyword", "")
    messageid = len(message_data)

    if typ == "質問する":
        ans, res = model.ask_answer(msg, category, keyword)
        put_message(res, sessionid, messageid)

    elif typ == "回答する":
        ans, judge = model.judge(msg, category, keyword)
        session["judged"] = True
        datastore_client.update_session_entity(
            sessionid=sessionid, judge=judge, rank=messageid - 1  # 最初のセリフ分
        )

    message_data.append(
        (
            (f"アキ{session['name']}", msg),
            ("ChatGPT", ans),
            len(message_data),
        )
    )

    session["messages"] = message_data

    return redirect(url_for("main.show"))
