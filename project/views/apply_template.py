from datetime import datetime
import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash
import json
import os
import requests
from project.__init__ import db
from project.forms import ConfirmForm, FilterForm, LeadForm, ApplyForm
from project.models import Template, db
from project import skiptracing as st
from project.models import Lead, Phone_Number, Email

apply = Blueprint("apply", __name__)


@apply.route("/apply/<selected>", methods=["GET", "POST"])
def main(selected):

    # this is bad code, and should be rewritten
    sel = []
    for s in selected:
        try:
            sel.append(int(s))
        except Exception:
            pass
    amount = len(sel)
    # for id_ in selected:
    #     classes.append(Lead.query.filter_by(id=id_).first())
    templates = Template.query.all()
    if request.method == "GET":
        print(f"selected: {selected}")
        print(f"templates: {templates}")
        return render_template(
            "apply_template.html", amount=amount, templates=templates
        )
    else:
        re = request.form.get("temp")
        if not re:
            flash("you must select a template")
            return render_template(
                "apply_template.html", amount=amount, templates=templates
            )
        return redirect(url_for("apply.confirm", selected=selected, re=re))


@apply.route("/confirm/<selected>/<re>", methods=["GET", "POST"])
def confirm(selected, re):
    sel = []
    for s in selected:
        try:
            sel.append(int(s))
        except Exception:
            pass
    amount = len(sel)
    example = Lead.query.filter_by(id=sel[0]).first()
    form_confirm = ConfirmForm()
    template = Template.query.filter_by(id=re).first()
    if request.method == "POST":
        messages = []
        for id_ in sel:
            recipient = Lead.query.filter_by(id=id_).first()
            for p in recipient.mobile_phones:
                text = translate(recipient, template.message)
                messages.append({"number": p.mobile_phone, "message": text})
                print(f"messages: {messages}")
        fail = 0
        for m in messages:
            try:
                send(m)
            except Exception as e:
                print(e)
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
    print(f'message: {message} || type(message): {type(message)}')
    print(f'os.getenv("TEXTBELT_API_KEY"): {os.getenv("TEXTBELT_API_KEY")}')
    r = requests.post(
        "https://textbelt.com/text",
        {
            # 'phone': f'2153171046',
            # "phone": message.number,
            "phone": "2062933922",
            "message": message["message"],
            "key": os.getenv("TEXTBELT_API_KEY"),
            "replyWebhookUrl": "http://756c-2601-989-4580-8ea0-c4c5-506e-e425-fad6.ngrok.io/textreply",
        },
    )
    print(f'r: {r.json()}')


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
    print(f"new_: {new_}")
    return new_
