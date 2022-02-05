import pandas as pd
import csv as csv_
from io import BytesIO
import zipfile

from flask import (
    Blueprint,
    request,
    render_template,
    flash,
    send_file,
)
from flask_login import login_required
from project.__init__ import db
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


@index.route("/")
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
                flash(e)
        return render_template("index.html")
    return render_template("index.html")


@index.route("/download")
@login_required
def dump_to_csv():

    dumps = {}
    models = [Users, Lead, Phone_Number, TextReply, Email, EmailReply, Template]
    for m in models:
        dumps[m.__name__] = {"type": m, "name": m.__name__}
    folder = BytesIO()
    with zipfile.ZipFile(folder, "w") as zip:
        print(f"dumps: {dumps}")
        for _, model in dumps.items():
            with open(f"{model['name']}.csv", "w") as dump:
                outcsv = csv_.writer(dump)
                outcsv.writerow([h for h in model["type"].__mapper__.columns])
                [
                    outcsv.writerow(
                        [
                            getattr(curr, column.name)
                            for column in model["type"].__mapper__.columns
                        ]
                    )
                    for curr in model["type"].query.all()
                ]
            _csv = open(f"{model['name']}.csv", "r")
            data = zipfile.ZipInfo(f"{model['name']}.csv")
            data.compress_type = zipfile.ZIP_DEFLATED
            zip.writestr(data, _csv.read())
    folder.seek(0)
    return send_file(folder, attachment_filename="Marketing_Concept_dumps.zip", as_attachment=True)
