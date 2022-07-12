import json
import os
import requests

from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import current_user, login_required

from project.helpers.db_session import db_session
from project.forms import ConfirmForm
from project.models import Template
from project.models import Lead, Addresses, Phone_Number

apply = Blueprint("apply", __name__)


@apply.route("/apply/<selected>", methods=["GET", "POST"])
@login_required
def main(selected: str):

    loaded: list = json.loads(selected)
    templates = Template.query.all()
    if request.method == "GET":
        return render_template(
            "apply_template.html", amount=len(loaded), templates=templates
        )
    else:
        temp_id = request.form.get("temp")
        if not temp_id:
            flash("you must select a template")
            return render_template(
                "apply_template.html", amount=len(loaded), templates=templates
            )
        return redirect(url_for("apply.confirm", selected=selected, temp_id=temp_id))


@apply.route("/confirm/<selected>/<temp_id>", methods=["GET", "POST"])
@login_required
def confirm(selected: str, temp_id: str):
    data = parse_selected(selected)
    template: Template = Template.query.get(temp_id)
    if request.method == "POST":
        fail = 0
        amount = 0
        with db_session():
            for pair in data:
                recipient: Lead = Lead.query.get(pair["lead_id"])
                address = Addresses.query.get(pair["address_id"])
                # TODO add option to send to all phone numbers or just primary number
                # TODO once primary number has been added to db
                if len(recipient.mobile_phones) > 0:
                    number: Phone_Number = recipient.mobile_phones[0]
                    text = translate(recipient, address, template.message)
                    try:
                        amount += 1
                        send({"number": number.mobile_phone, "message": text})
                    except Exception as e:
                        # TODO change this to logging
                        fail += 1
                        print(f"e: {e}")
                    recipient.template_sent = template.name
        if fail > 0:
            flash(
                f"out of {amount} messages attempted, {fail} failed. see terminal for details"
            )
        else:
            flash(f"{amount} messages sent successfully")
        return redirect(url_for("leads.main"))
    return render_template(
        "apply_confirm.html",
        amount=len(data),
        template=template,
        form_confirm=ConfirmForm(),
        example=Lead.query.get(data[0]["lead_id"]),
    )


def parse_selected(selected: str) -> list:
    """parses incoming data into dictionaries"""
    loaded = json.loads(selected)
    data = []
    for pair in loaded:
        pair: str
        split: list = pair.split("_")
        data.append({"lead_id": split[0], "address_id": split[1]})
    return data


def send(message):
    """sends the message to text belt to send"""
    # commented out lines are for testing
    # TODO add WEBHOOK to .env file to eliminate this if/else
    if os.environ.get("_HEROKU_HOSTING"):
        webhook = os.getenv("WEBHOOK")
    else:
        webhook = "http://4bc3-72-228-49-124.ngrok.io/textreply"
    print(f'sending: {message["message"]} to {message["number"]}')
    r = requests.post(
        "https://textbelt.com/text",
        {
            # 'phone': f'2153171046',
            # "phone": message["number"],
            "phone": "2062933922",
            "message": message["message"],
            # "key": os.getenv("TEXTBELT_API_KEY"),
            "key": os.getenv("TEXTBELT_API_KEY") + "_test", #use for testing. doesen't send
            "replyWebhookUrl": webhook,
        },
    )
    current_user.texts_left = r.json()["quotaRemaining"]


def translate(recipient: Lead, address: Addresses, template: str) -> str:
    """replaces custom variables with values from the database"""
    FNAME = "|First_Name|"
    LNAME = "|Last_Name|"
    AGE = "|Age|"
    ADDRESS = "|Address|"
    CITY = "|City|"
    STATE = "|State|"
    ZIP = "|zip|"

    _fname = recipient.first_name if recipient.first_name != None else ""
    _lname = recipient.last_name if recipient.last_name != None else ""
    _age = recipient.age if recipient.age != None else ""
    _address = address.address if address.address != None else ""
    _city = address.city if address.city != None else ""
    _state = address.state if address.state != None else ""
    _zip = address.zip if address.zip != None else ""

    new_ = (
        template.replace(FNAME, _fname)
        .replace(LNAME, _lname)
        .replace(AGE, _age)
        .replace(ADDRESS, _address)
        .replace(CITY, _city)
        .replace(STATE, _state)
        .replace(ZIP, _zip)
    )
    return new_
