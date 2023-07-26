import os

from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.chatgpt import ChatGPT

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

    message_data = session["messages"]

    msg = f"Login ID: {session['id']}"
    return render_template(
        "main.html",
        title="逆アキネイター(仮)",
        message=msg,
        data=message_data,
    )


@view.route("/", methods=["POST"])
def post():
    msg = request.form.get("comment")
    typ = request.form.get("action")

    if typ == "リセット":
        session["messages"] = []
        return redirect(url_for("main.show"))

    if typ == "質問する":
        ans = model.ask_answer(msg)
    elif typ == "回答する":
        ans = model.judge(msg)

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
