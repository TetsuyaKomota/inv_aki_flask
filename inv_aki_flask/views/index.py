from datetime import datetime

from flask import Blueprint, render_template

view = Blueprint("index", __name__, url_prefix="/")


@view.route("/", methods=["GET"])
def show():
    yyyymmdd = datetime.now().strftime("%Y%m%d")
    return render_template("index.html", name=yyyymmdd)
