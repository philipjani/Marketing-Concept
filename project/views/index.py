import pandas as pd
import csv as csv_
from io import BytesIO
import zipfile
import tempfile
from flask import (
    Blueprint,
    redirect,
    request,
    render_template,
    flash,
    send_file,
    url_for,
)
from flask_login import login_required
from project.__init__ import db
from project.helpers.db_session import db_session
from project.models import (
    Users,
    Phone_Number,
    TextReply,
    Email,
    EmailReply,
    Template,
    Lead,
)

index = Blueprint("index", __name__)


@index.route("/", methods=["GET", "POST"])
@login_required
def page():
    if request.method == "POST":
        f = request.files["file"]
        if f.filename != "":
            try:
                df = pd.read_csv(f.stream)
                con = db.engine
                df.to_sql("lead", con, if_exists="append", index=False)
                flash("csv uploaded successfully")
            except Exception as e:
                flash(f"e: {e}")
    return render_template("index.html")

@index.route("/delete")
@login_required
def delete():
    with db_session() as sess:
        delete = Lead.query.all()
        for lead in delete:
            sess.delete(lead)
    return redirect(url_for("index.page"))

@index.route("/download")
@login_required
def dump_to_csv():

    dumps = {}
    models = [Users, Lead, Phone_Number, TextReply, Email, EmailReply, Template]
    for m in models:
        headers = [c.name for c in m.__mapper__.columns]
        for i, h in enumerate(headers):
            if h == "id":
                headers.pop(i)
        dumps[m.__name__] = {"type": m, "name": m.__name__, "headers": headers}
    folder = BytesIO()
    with zipfile.ZipFile(folder, "w") as zip:

        for _, model in dumps.items():
            with tempfile.SpooledTemporaryFile(mode="w") as dump:
                outcsv = csv_.writer(dump)
                outcsv.writerow([h for h in model["headers"]])
                [
                    outcsv.writerow(
                        [getattr(curr, column) for column in model["headers"]]
                    )
                    for curr in model["type"].query.all()
                ]

                dump.seek(0)
                data = zipfile.ZipInfo(f"{model['name']}.csv")
                data.compress_type = zipfile.ZIP_DEFLATED
                zip.writestr(data, dump.read())
    folder.seek(0)
    return send_file(
        folder, attachment_filename="Marketing_Concept_dumps.zip", as_attachment=True
    )
