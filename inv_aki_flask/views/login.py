from flask import Blueprint, redirect, render_template, request, session

from inv_aki_flask.model.secret_client import SecretClient

view = Blueprint("login", __name__, url_prefix="/login")

secret_client = SecretClient(project_id="inv-aki")


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
    id = request.form.get("id")
    pswd = request.form.get("pass")

    session["login"] = pswd == secret_client.get_secret("login_pswd")

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
