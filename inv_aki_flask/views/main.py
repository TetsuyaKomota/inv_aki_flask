from flask import Blueprint, redirect, render_template, request, session

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
        return redirect("/main/login")


@view.route("/", methods=["POST"])
def form():
    global message_data
    msg = request.form.get("comment")
    message_data.append((session["id"], msg))
    message_data = message_data[-25:]
    return redirect("/main/")


@view.route("/login", methods=["GET"])
def login():
    return render_template(
        "login.html",
        title="Login",
        err=False,
        message="IDとパスワードを入力: ",
        id="",
    )


@view.route("/login", methods=["POST"])
def login_post():
    global member_data
    id = request.form.get("id")
    pswd = request.form.get("pass")

    if id in member_data:
        session["login"] = pswd == member_data[id]
    else:
        member_data[id] = pswd
        session["login"] = True

    session["id"] = id

    if session["login"]:
        return redirect("/main/")
    else:
        return render_template(
            "login.html",
            title="Login",
            err=False,
            message="パスワードが違います",
            id=id,
        )


@view.route("/logout", methods=["GET"])
def logout():
    session.pop("id")
    session.pop("login")
    return redirect("/main/login")
