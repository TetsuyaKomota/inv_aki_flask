import os

from flask import Blueprint, redirect, render_template, request, session, url_for

from inv_aki_flask.model.chatgpt import ChatGPT

view = Blueprint("main", __name__, url_prefix="/main")

member_data = {}

message_data = []

if os.path.exists("tmp/api_key.txt"):
    with open("tmp/api_key.txt", "r") as f:
        api_key = f.read().strip()
    model = ChatGPT(api_key, "")
else:
    model = ChatGPT()


@view.route("/", methods=["GET"])
def show():
    global message_data
    if "login" in session and session["login"]:
        msg = f"Login ID: {session['id']}"
        return render_template(
            "main.html",
            title="逆アキネイター(仮)",
            message=msg,
            data=message_data,
        )
    else:
        return redirect(url_for("login.show"))


@view.route("/", methods=["POST"])
def post():
    global message_data
    msg = request.form.get("comment")
    typ = request.form.get("action")[:-2]

    if typ == "質問":
        ans = model.ask_answer(msg)
    elif typ == "回答":
        ans = model.judge(msg)

    message_data.append((session["id"], typ + ":" + msg + ":" + ans))
    message_data = message_data[-25:]
    return redirect(url_for("main.show"))