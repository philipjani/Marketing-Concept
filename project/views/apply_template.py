from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required
import os
import requests
from project.forms import ConfirmForm
from project.models import Template
from project.models import Lead

apply = Blueprint("apply", __name__)


@apply.route("/apply/<selected>", methods=["GET", "POST"])
@login_required
def main(selected):

    # this try/except is bad code, and should be rewritten but I wrote it quickly
    symbols = ["["," ","'",",","]"]
    sel = []
    tmp = ""
    for s in selected:
        if s in symbols:
            if tmp != "":
                sel.append(int(tmp))
                tmp = ""
        else:
            tmp += s

    try:
        sel.append(int(tmp))
    except Exception:
        pass
    amount = len(sel)
    templates = Template.query.all()
    if request.method == "GET":
        return render_template(
            "apply_template.html", amount=amount, templates=templates
        )
    else:
        temp_id = request.form.get("temp")
        if not temp_id:
            flash("you must select a template")
            return render_template(
                "apply_template.html", amount=amount, templates=templates
            )
        return redirect(url_for("apply.confirm", selected=selected, temp_id=temp_id))


@apply.route("/confirm/<selected>/<temp_id>", methods=["GET", "POST"])
@login_required
def confirm(selected, temp_id):
    symbols = ["["," ","'",",","]"]
    sel = []
    tmp = ""
    for s in selected:
        if s in symbols:
            if tmp != "":
                sel.append(int(tmp))
                tmp = ""
        else:
            tmp += s
    try:
        sel.append(int(tmp))
    except Exception:
        pass
    amount = len(sel)
    example = Lead.query.filter_by(id=sel[0]).first()
    form_confirm = ConfirmForm()
    template = Template.query.filter_by(id=temp_id).first()
    if request.method == "POST":
        messages = []
        for id_ in sel:
            recipient = Lead.query.filter_by(id=id_).first()
            for p in recipient.mobile_phones:
                text = translate(recipient, template.message)
                messages.append({"number": p.mobile_phone, "message": text})
                
        fail = 0
        for m in messages:
            try:
                send(m)
            except Exception as e:
                fail += 1
        if fail > 0:
            flash(
                f"out of {amount} messages attempted, {fail} failed. see terminal for details"
            )
        else:
            flash(f"{amount} messages sent successfully")
        return redirect(url_for("leads.main"))
    return render_template(
        "apply_confirm.html",
        amount=amount,
        template=template,
        form_confirm=form_confirm,
        example=example,
    )


def send(message):
    if os.environ.get("_HEROKU_HOSTING"):
        webhook = os.getenv("WEBHOOK")
    else:
        webhook = "http://4bc3-72-228-49-124.ngrok.io/textreply"
    r = requests.post(
        "https://textbelt.com/text",
        {
            'phone': f'2153171046',
            # "phone": message["number"],
            # "phone": "2062933922",
            "message": message["message"],
            "key": os.getenv("TEXTBELT_API_KEY"),
            # "key": os.getenv("TEXTBELT_API_KEY") + "_test", #use for testing. doesen't send 

            "replyWebhookUrl": webhook,
        },
    )


def translate(target, template: str) -> str:
    """replaces custom variables with values from the database"""
    FNAME = "TtTfnameTtT"
    LNAME = "TtTlnameTtT"
    AGE = "TtTageTtT"
    ADDRESS = "TtTaddressTtT"
    CITY = "TtTcityTtT"
    STATE = "TtTstateTtT"
    ZIP = "TtTzipTtT"
    new_ = (
        template.replace(FNAME, target.first_name)
        .replace(LNAME, target.last_name)
        .replace(AGE, str(target.age))
        .replace(ADDRESS, target.address)
        .replace(CITY, target.city)
        .replace(STATE, target.state)
        .replace(ZIP, target.zip)
    )
    return new_
