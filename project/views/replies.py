
from flask import Blueprint, render_template
from flask_login import login_required
import pytz
from project.models import Phone_Number, TextReply, Lead

replies = Blueprint("replies", __name__)

@replies.route('/replies', methods=["GET", 'POST'])
@login_required
def main():
    replies = TextReply.query.all()
    for r in replies:
        num = Phone_Number.query.get(r.phone_id)
        lead = Lead.query.get(num.lead_id)
        r.additional["address"] = lead.address
        r.additional["city"] = lead.city
        r.additional["state"] = lead.state
        r.additional["zip"] = lead.zip
        r.additional["first_name"] = lead.first_name
        r.additional["last_name"] = lead.last_name
        r.additional["property_type"] = lead.property_type
        r.additional["mls_status"] = lead.mls_status
        r.additional["template_sent"] = lead.template_sent
        r.additional["number"] = num.mobile_phone
        r.additional["date"] = convert_date(r.contact_time)
        r.additional["time"] = convert_time(r.contact_time)
    return render_template("replies.html", replies=replies)

def convert_date(time):
    est = pytz.timezone('US/Eastern')
    fmt = "%m-%d-%Y"
    return time.astimezone(est).strftime(fmt)
    
def convert_time(time):
    est = pytz.timezone('US/Eastern')
    fmt = "%I:%M %p"
    return time.astimezone(est).strftime(fmt)