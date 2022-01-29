from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from flask_login import login_required

from project.forms import Login
from project.models import Users

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = Login()
    if request.method == "GET":
        if current_user.is_active:
            return redirect(url_for("index.page"))
        return render_template("login.html", form=form)
    if form.validate_on_submit():
        user = Users.query.filter_by(name=form.name.data).first()
        login_user(user, remember=form.remember.data)
        return redirect(url_for("index.page"))
    return render_template("login.html", form=form)

@auth.route("/logout", methods=["GET"])
@login_required
def logout():
    flash("Successfully logged out")
    logout_user()
    return redirect(url_for("auth.login"))

