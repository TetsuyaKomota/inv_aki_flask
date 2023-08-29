from datetime import datetime

from flask import Blueprint, redirect, render_template, url_for

view = Blueprint("index", __name__, url_prefix="/")


@view.route("/", methods=["GET"])
def show():
    return redirect(url_for("main.show"))
