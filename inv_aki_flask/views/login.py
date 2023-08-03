from flask import Blueprint, redirect, render_template, request, session

from inv_aki_flask.model.secret_client import SecretClient

view = Blueprint("login", __name__, url_prefix="/login")

secret_client = SecretClient(project_id="inv-aki")

login_pswd = secret_client.get_secret("login_pswd")


@view.route("/", methods=["GET"])
def show():
    return render_template(
        "login.html",
        title="ログイン画面",
        err=False,
        message="名前とパスワードを入力してください",
        id="",
    )


@view.route("/", methods=["POST"])
def post():
    id = request.form.get("id")
    pswd = request.form.get("pass")

    session["login"] = False
    if id == "":
        msg = "名前を入力してください"
    elif pswd != login_pswd:
        msg = "パスワードが違います"
    else:
        session["login"] = True

    # 名前を変更した際に，変更前の履歴が残っている場合は削除する
    if "messages" in session and session.get("id", "") != id:
        session.pop("messages")

    session["id"] = id

    if session["login"]:
        return redirect("/main/")
    else:
        return render_template(
            "login.html",
            title="ログイン画面",
            err=False,
            message=msg,
            id=id,
        )


@view.route("/logout", methods=["GET"])
def logout():
    session.pop("login")
    return redirect("/main/")
