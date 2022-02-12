from flask import Blueprint, render_template
from flask_login import login_required
import pytz
from project.models import Phone_Number, TextReply, Lead

replies = Blueprint("replies", __name__)


@replies.route("/replies", methods=["GET", "POST"])
@login_required
def main():
    _replies = TextReply.query.all()
    print(f"replies: {_replies}")
    replies = []
    for r in _replies:
        num = Phone_Number.query.get(r.phone_id)
        lead = Lead.query.get(num.lead_id)
        replies.append(
            {"address": lead.address,
                "id": r.id,
                "message": r.message,
                "city": lead.city,
                "state": lead.state,
                "zip": lead.zip,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "property_type": lead.property_type,
                "mls_status": lead.mls_status,
                "template_sent": lead.template_sent,
                "number": num.mobile_phone,
                "date": convert_date(r.contact_time),
                "time": convert_time(r.contact_time),
            }
        )
    return render_template("replies.html", replies=replies)


def convert_date(time):
    est = pytz.timezone("US/Eastern")
    fmt = "%m-%d-%Y"
    return time.astimezone(est).strftime(fmt)


def convert_time(time):
    est = pytz.timezone("US/Eastern")
    fmt = "%I:%M %p"
    return time.astimezone(est).strftime(fmt)
