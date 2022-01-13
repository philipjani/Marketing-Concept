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
        print(f'messages: {messages}')
        flash(f"{amount} messages sent")
    return render_template(
        "apply_confirm.html",
        amount=amount,
        template=template,
        form_confirm=form_confirm,
        example=example,
    )


def translate(target, template: str) -> str:
    """replaces custom variables with values from the database"""
    print(f'target: {target} || type(target): {type(target)}')
    print(f'template: {template}')
    FNAME = "ttttttfnametttttt"
    LNAME = "ttttttlnametttttt"
    AGE = "ttttttagetttttt"
    ADDRESS = "ttttttaddresstttttt"
    CITY = "ttttttcitytttttt"
    STATE = "ttttttstatetttttt"
    ZIP = "ttttttziptttttt"
    print(f'target.first_name: {target.first_name} || type(target.first_name): {type(target.first_name)}')
    new_ = (
        template.replace(FNAME, target.first_name)
        .replace(LNAME, target.last_name)
        .replace(AGE, str(target.age))
        .replace(ADDRESS, target.address)
        .replace(CITY, target.city)
        .replace(STATE, target.state)
        .replace(ZIP, target.zip)
    )
    print(f'new_: {new_}')
    return new_
