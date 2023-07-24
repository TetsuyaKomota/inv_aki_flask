from datetime import datetime

from google.cloud import secretmanager

from flask import Blueprint, render_template

view = Blueprint("index", __name__, url_prefix="/")

# FIXME SecretManager の検証
project_id = "inv_aki"
secret_id = "hello"
version_id = "latest"
client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

response = client.access_secret_version(request={"name": name})
payload = response.payload.data.decode("utf-8")

@view.route("/", methods=["GET"])
def show():
    yyyymmdd = datetime.now().strftime("%Y%m%d")
    return render_template("index.html", name=yyyymmdd, payload=payload)
