from flask import Blueprint, render_template

view = Blueprint("index", __name__, url_prefix="/")


@view.route("/", methods=["GET"])
def show():
    return render_template("index.html", name="APP ENGINE")
