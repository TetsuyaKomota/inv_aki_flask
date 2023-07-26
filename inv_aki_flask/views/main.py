import os

from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.chatgpt import MAX_QUESTIONS, ChatGPT

view = Blueprint("main", __name__, url_prefix="/main")

if os.path.exists("tmp/api_key.txt"):
    with open("tmp/api_key.txt", "r") as f:
        api_key = f.read().strip()
    model = ChatGPT(api_key, "")
else:
    model = ChatGPT()


@view.route("/", methods=["GET"])
def show():
    if not session.get("login", False):
        return redirect(url_for("login.show"))

    if "messages" not in session:
        session["messages"] = []

    if "keyword" not in session:
        work, keyword = model.select_keyword()
        session["work"] = work
        session["keyword"] = keyword

    message_data = session["messages"]
    judged = "judged" in session

    msg = f"Login ID: {session['id']}"
    return render_template(
        "main.html",
        title="逆アキネイター(仮)",
        message=msg,
        data=message_data,
        ans_count=len(message_data),
        max_count=MAX_QUESTIONS,
        judged=judged,
    )


@view.route("/", methods=["POST"])
def post():
    msg = request.form.get("comment")
    typ = request.form.get("action")

    if typ == "リセット":
        for k in ["messages", "work", "keyword", "judged"]:
            if k in session:
                del session[k]
        return redirect(url_for("main.show"))

    work = session.get("work", "")
    keyword = session.get("keyword", "")

    if typ == "質問する":
        ans = model.ask_answer(msg, work, keyword)
    elif typ == "回答する":
        session["judged"] = True
        ans = model.judge(msg, work, keyword)

    if "messages" not in session:
        session["messages"] = []

    message_data = session["messages"]

    message_data.append(
        (
            (f"アキ{session['id']}", msg),
            ("ChatGPT", ans),
            len(message_data) + 1,
        )
    )

    session["messages"] = message_data

    return redirect(url_for("main.show"))
