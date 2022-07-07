import pandas as pd
from sqlalchemy.orm.scoping import scoped_session
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
import math

index = Blueprint("index", __name__)


@index.route("/", methods=["GET", "POST"])
@login_required
def page():
    if request.method == "POST":
        f = request.files["file"]
        if f.filename != "":
            try:
                with db_session() as sess:
                    upload(pd.read_csv(f.stream), sess)
            except Exception as e:
                flash(f"e: {e}")
                raise
    return render_template("index.html")


def upload(df: pd.DataFrame, session: scoped_session):
    from project.models import Addresses, Lead

    fails = 0
    successes = 0
    for _, row in df.iterrows():
        try:
            d = row.to_dict()
            for k, v in d.items():
                if type(v) != str and math.isnan(v):
                    d[k] = None
            if not Addresses.query.filter_by(
                address=d["address"], city=d["city"], state=d["state"]
            ).first():
                address = Addresses(
                    address=d["address"],
                    city=d["city"],
                    state=d["state"],
                    zip=d["zip"],
                    owner_occupied=d["owner_occupied"],
                    property_type=d["property_type"],
                )
            # !bug this could be an issue if there are two different people with the same name in the database
            # !bug the way to fix it is to automatically skiptrace them
            lead = Lead.query.filter_by(
                first_name=d["first_name"], last_name=d["last_name"]
            ).first()
            if not lead:
                lead = Lead(
                    first_name=d["first_name"],
                    last_name=d["last_name"],
                )
                if d["phone_number"]:
                    phone = Phone_Number.query.filter_by(mobile_phone=d["phone_number"]).first()
                    if phone is None:
                        phone = Phone_Number(mobile_phone=d["phone_number"])
                    lead.mobile_phones.append(phone)
            lead.addresses.append(address)
            session.add(lead)
            successes += 1
        except ValueError:
            # TODO add logger and custom Exceptions
            fails += 1
            print(f"unable to add{row}")
    if successes > 0:
        flash(f"uploaded {successes} new addresses successfully.")
    else:
        flash("No new Addresses found within csv")
    if fails:
        # TODO remove after logger installed
        flash(f"{fails} were unable to be added due to unrecognized column names")


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
