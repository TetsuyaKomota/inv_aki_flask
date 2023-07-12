from datetime import datetime

from flask import Blueprint, render_template

view = Blueprint("main", __name__, url_prefix="/main")


@view.route("/", methods=["GET"])
def show():
    return render_template("main.html")
