import base64
from flask_sqlalchemy import SQLAlchemy
from os import environ
from sqlalchemy import create_engine
import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash

from project.models import db
from project import skiptracing as st
from project.models import Lead, Template, TextReply

index = Blueprint("index", __name__)


@index.route("/", methods=["GET", "POST"])
def page():

    if request.method == "POST":
        from project.__init__ import db
        f = request.files["file"]
        if f.filename != "":
            df = pd.read_csv(f.stream)
            con = db.engine
            df.to_sql("lead", con, if_exists="append", index=False)
            flash("csv uploaded successfully")
        return redirect(url_for("index.page"))
    else:
        return render_template("index.html")
