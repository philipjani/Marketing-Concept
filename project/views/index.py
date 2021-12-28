import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash

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
