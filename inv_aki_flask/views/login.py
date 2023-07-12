from flask import Blueprint, redirect, render_template, request, session

view = Blueprint("login", __name__, url_prefix="/login")

member_data = {}

message_data = []


@view.route("/", methods=["GET"])
def show():
    return render_template(
        "login.html",
        title="Login",
        err=False,
        message="IDとパスワードを入力: ",
        id="",
    )


@view.route("/", methods=["POST"])
def post():
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
    return redirect("/main/")
