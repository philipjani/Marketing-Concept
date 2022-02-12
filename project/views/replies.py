
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required

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
    return render_template("replies.html", replies=replies)
