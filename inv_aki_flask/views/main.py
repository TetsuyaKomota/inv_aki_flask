from flask import Blueprint, redirect, render_template, request, session, url_for

view = Blueprint("main", __name__, url_prefix="/main")

member_data = {}

message_data = []


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
    message_data.append((session["id"], msg))
    message_data = message_data[-25:]
    return redirect(url_for("main.show"))
