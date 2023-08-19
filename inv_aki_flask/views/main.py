import os
from datetime import datetime
from hashlib import md5

from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.chatgpt import MAX_QUESTIONS, ChatGPT
from inv_aki_flask.model.datastore_client.message import client as message_entity_client
from inv_aki_flask.model.datastore_client.session import client as session_entity_client

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
    session_entity_client.create_session_entity(
        sessionid, category=category, keyword=keyword
    )


def put_message(res, sessionid, messageid):
    message_entity_client.create_message_entity(
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

    notice = session.get("notice", "")

    viewad = session.get("viewad", False)
    ans_count = len(message_data) - 1  # 最初のセリフ分
    if viewad:
        max_count = MAX_QUESTIONS * 2
    else:
        max_count = MAX_QUESTIONS

    return render_template(
        "main.html",
        title="逆アキネイター",
        message=msg,
        data=message_data,
        ans_count=ans_count,
        max_count=max_count,
        ad_disabled="disabled" if viewad else "",
        judged=judged,
        input_text=input_text,
        notice=notice,
    )


@view.route("/", methods=["POST"])
def post():
    if "login" not in session or "name" not in session:
        return redirect(url_for("login.show"))

    msg = request.form.get("comment")
    typ = request.form.get("action")

    sessionid = session.get("sessionid", "")

    if typ == "答え合わせする":
        return redirect(url_for("result.show", sessionid=sessionid))

    if typ == "広告を視聴して質問回数を増やす":
        session["viewad"] = True
        return redirect(url_for("main.show"))

    if typ == "リセット":
        for k in ["messages", "category", "keyword", "judged", "notice", "viewed"]:
            if k in session:
                del session[k]
        return redirect(url_for("main.show"))

    # comment が空の場合は警告出す
    if not msg:
        if typ == "質問する":
            target = "質問"
        elif typ == "回答する":
            target = "キーワード"
        session["notice"] = f"{target}を入力してください"
        return redirect(url_for("main.show"))
    else:
        if "notice" in session:
            del session["notice"]

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
        session["judged"] = True
        ans, res = model.judge(msg, category, keyword)

        answer = msg
        explain1 = res.get("explain1", None)
        explain2 = res.get("explain2", None)
        reason = res.get("reason", None)
        judge = ans.startswith("正解！")

        session_entity_client.update_session_entity(
            sessionid=sessionid,
            count=messageid - 1,  # 最初のセリフ分
            answer=answer,
            explain1=explain1,
            explain2=explain2,
            reason=reason,
            judge=judge,
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
