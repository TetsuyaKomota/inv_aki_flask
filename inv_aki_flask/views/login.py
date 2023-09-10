from flask import Blueprint, redirect, render_template, request, session

from inv_aki_flask.model.inner_session import (
    get_name,
    is_login,
    pop_sessionid,
    set_login,
    set_logout,
    set_name,
)
from inv_aki_flask.model.secret_client import SecretClient

view = Blueprint("login", __name__, url_prefix="/login")

secret_client = SecretClient(project_id="inv-aki")

login_pswd = secret_client.get_secret("login_pswd")


@view.route("/", methods=["GET"])
def show():
    name = get_name(session)
    return render_template(
        "login.html",
        err=False,
        message="名前を入力してください",
        name=name,
    )


@view.route("/", methods=["POST"])
def post():
    name = request.form.get("name")
    # pswd = request.form.get("pass")
    pswd = login_pswd  # パスワードが必要な場合は修正

    set_logout(session)
    if name == "":
        msg = "名前を入力してください"
    elif pswd != login_pswd:
        msg = "パスワードが違います"
    else:
        set_login(session)

    # 名前を変更した際に，変更前の履歴が残っている場合は削除する
    if get_name(session) != name:
        pop_sessionid(session)

    set_name(session, name)

    if is_login(session):
        return redirect("/main/")
    else:
        return render_template(
            "login.html",
            err=False,
            message=msg,
            name=name,
        )


@view.route("/logout", methods=["GET"])
def logout():
    set_logout(session)
    return redirect("/main/")
