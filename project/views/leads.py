from datetime import datetime
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required
import json
import os
import requests
from project.__init__ import db
from project.forms import ApplyForm, FilterForm, LeadForm
from project.helpers.db_session import db_session
from project.models import db
from project.models import Lead, Phone_Number, Email

leads = Blueprint("leads", __name__)


@leads.route("/leads", methods=["POST", "GET"])
@login_required
def main():
    filter_form = FilterForm()
    lead_form = LeadForm()
    apply_form = ApplyForm()
    filter_form.comp_select.choices = [
        "last_name",
        "city",
        "zip",
        "owner_occupied",
        "property_type",
        "mls_status",
    ]

    if request.method == "POST":
        with db_session(autocommit=False) as sess:
            selected = request.form.getlist("select")
            print(f'selected: {selected}')
            if filter_form.filter_submit.data:
                column = filter_form.comp_select.data
                data = filter_form.info.data
                rows = filter_form.length.data
                leads_ = filter(column, data, rows)
                return render(lead_form, leads_, filter_form, apply_form)
            if lead_form.lead_submit.data:
                skipped_int = 0
                success = 0
                final_msg = ''
                ids = [int(i) for i in selected]
                leads_ = db.session.query(Lead).filter(Lead.id.in_(ids)).all()
                for lead in leads_:
                    #     # API call does not work without first name, OR if already have phone/emails
                    if not lead.first_name:
                        skipped_int += 1
                        final_msg += f'skipping "{lead.first_name} {lead.last_name}" due to lack of information<br>'
                        continue
                    if lead.mobile_phones or lead.emails:
                        skipped_int += 1
                        final_msg += f'skipping "{lead.first_name} {lead.last_name}" due to already having phone/email<br>'
                        continue
                    if lead.last_trace is not None:
                        skipped_int += 1
                        final_msg += f'skipping "{lead.first_name} {lead.last_name}" due already being traced<br>'
                        continue
                    lead_dict = get_lead_dict(lead)
                    person_data = get_pf_api_data(lead_dict)
                    if person_data:
                        age, mobile_phones, emails = extract_info_from_person_data(
                            person_data
                        )
                        update_person_db(db, lead, age, mobile_phones, emails, sess)
                        success += 1
                    else:
                        final_msg += f'"{lead.first_name} {lead.last_name}" trace returned "No strong Matches<br>'
                        lead.last_trace = datetime.utcnow()
                final_msg = final_msg[:-len("<br>")] if final_msg != '' else "all traces successful"
                flash(final_msg)
                try:
                    sess.commit()
                    flash(
                        f"traced {success} leads successfully. skipped {skipped_int} traces."
                    )
                except Exception as e:
                    flash(
                        "There was an error inserting API data into database."
                    )
                    print(e)
                page = request.args.get("page", 1, type=int)
                leads_ = (
                    db.session.query(Lead)
                    .order_by(Lead.id)
                    .paginate(page=page, per_page=10)
                )
                if apply_form.apply_submit.data:
                    if selected:
                        return redirect(url_for("apply.main", selected=selected))
                    else:
                        return redirect(url_for("leads.main"))
                return render(lead_form, leads_, filter_form, apply_form)
    if request.method == "GET":
        page = request.args.get("page", 1, type=int)
        leads_ = (
            db.session.query(Lead).order_by(Lead.id).paginate(page=page, per_page=10)
        )
    return render(lead_form, leads_, filter_form, apply_form)


def render(lead_form, leads_, filter_form, apply_form):
    return render_template(
        "leads.html",
        lead_form=lead_form,
        leads=leads_,
        filter_form=filter_form,
        apply_form=apply_form,
    )

def extract_info_from_person_data(person_data):
    age = (
        person_data["person"]["age"]
        if person_data["person"]["age"] != ""
        else "Unknown"
    )
    email_data = person_data["person"]["emails"]
    emails = [x["email"] for x in email_data]
    phone_data = person_data["person"]["phones"]
    mobile_phones = [
        x["number"]
        for x in phone_data
        if x["type"] == "mobile"
        and x["isConnected"] == True
        and int(x["lastReportedDate"].split("/")[2]) > 2015
    ]
    return age, mobile_phones, emails


def get_pf_api_data(lead_dict):

    payload = json.dumps(lead_dict)
    headers = {
        "Content-Type": "application/json",
        "galaxy-ap-name": os.environ.get("PEOPLE_API_NAME"),
        "galaxy-ap-password": os.environ.get("PEOPLE_API_PASS"),
        "galaxy-search-type": "DevAPIContactEnrich",
    }
    r = requests.post(
        "https://api.peoplefinderspro.com/contact/enrich", data=payload, headers=headers
    )
    response_body = r.text
    person_data = json.loads(response_body)
    if not "person" in person_data.keys():
        return False
    person_data = r.json()
    return person_data


def update_person_db(db, lead, age, mobile_phones, emails, session):
    # Insert all phone numbers of lead into phone numbers table
    for phone in mobile_phones:
        new = Phone_Number(mobile_phone=phone, lead_id=lead.id)
        session.add(new)
    for email in emails:
        new = Email(email_address=email, lead_id=lead.id)
        session.add(new)
    lead.age = age
    lead.last_trace = datetime.utcnow()

def get_lead_dict(lead):
    lead_dict = {
        "FirstName": lead.first_name,
        "LastName": lead.last_name,
        "Address": {
            "addressLine1": lead.address,
            "addressLine2": f"{lead.city}, {lead.state}",
        },
    }
    return lead_dict

def filter(category, query_string, rows):
    page = request.args.get("page", 1, type=int)
    leads = (
        db.session.query(Lead)
        .filter(getattr(Lead, category).like(f"%{query_string}%"))
        .paginate(page=page, per_page=rows)
    )
    return leads
