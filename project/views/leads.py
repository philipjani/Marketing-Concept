from datetime import datetime
import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required
import json
import os
import requests
from project.__init__ import db
from project.forms import ApplyForm, FilterForm, LeadForm
from project.models import db
from project import skiptracing as st
from project.models import Lead, Phone_Number, Email

leads = Blueprint("leads", __name__)



@leads.route("/leads", methods=["POST", "GET"])
@login_required
def main():
    print(f'test')
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
        selected = request.form.getlist('select')
        print(f'selected: {selected}')
        if filter_form.filter_submit.data:
            column = filter_form.comp_select.data
            data = filter_form.info.data
            rows = filter_form.length.data
            leads_ = filter(column, data, rows)
        if lead_form.lead_submit.data:
            leads_ = retrieve_selected_leads(db, selected)
            skipped_int = 0
            success = 0
            for lead in leads_:
            #     # API call does not work without first name, OR if already have phone/emails
                if not lead.first_name:
                    skipped_int += 1
                    print(f'skipping due to lack of information: {lead}')
                    continue
                if lead.mobile_phones or lead.emails:
                    skipped_int += 1
                    print(f'skipping due to already having phone/email: {lead}')
                    continue
                # if lead.last_trace is not None:
                #     skipped_int += 1
                #     print(f'skipping due already being traced: {lead}')
                #     continue
                lead_dict = get_lead_dict(lead)
                person_data = get_pf_api_data(lead_dict)
                # print(f'person_data: {person_data}')
                if person_data:
                    age, mobile_phones, emails = extract_info_from_person_data(person_data)
                    update_person_db(db, lead, age, mobile_phones, emails)
                    success += 1
                else:
                    print(f'trace returned "No strong Matches: {lead}')
                    lead.last_trace = datetime.utcnow()
            try:
                db.session.commit()
                flash(f"traced {success} leads successfully. skipped {skipped_int} traces. see terminal for details")
            except Exception as e:
                flash("There was an error inserting API data into database. exception printed to terminal")
                print(e)
            page = request.args.get("page", 1, type=int)
            leads_ = db.session.query(Lead).order_by(Lead.id).paginate(page=page, per_page=10)
        if apply_form.apply_submit.data:
            if selected:
                return redirect(url_for("apply.main", selected=selected))
            else:
                return redirect(url_for("leads.main"))
    if request.method == "GET":
        page = request.args.get("page", 1, type=int)
        leads_ = db.session.query(Lead).order_by(Lead.id).paginate(page=page, per_page=10)
    return render_template(
        "leads.html", lead_form=lead_form, leads=leads_, filter_form=filter_form, apply_form=apply_form
    )


def convert_lead_ids_to_ints(lead_ids):
    ints_selected = []
    for id_num in lead_ids:
        ints_selected.append(int(id_num))
    tuple_selected = tuple(ints_selected)
    return tuple_selected

def extract_info_from_person_data(person_data):
    # first_name = person_data['person']['name']['firstName']
    # last_name = person_data['person']['name']['lastName']
    # middle_name = person_data['person']['name']['middleName']
    print(f'person_data: {person_data}')
    age = person_data['person']['age']
    print(f'age: {age} || type(age): {type(age)}')
    try:
        age = int(age)
    except Exception:
        age = -1
    email_data = person_data['person']['emails']
    emails = [x['email'] for x in email_data]
    phone_data = person_data['person']['phones']
    mobile_phones = [x['number'] for x in phone_data if x['type'] == 'mobile' and x['isConnected'] == True and int(x['lastReportedDate'].split('/')[2]) > 2015]
    return age, mobile_phones, emails

def get_pf_api_data(lead_dict):

    payload = json.dumps(lead_dict)

    headers = {
        'Content-Type': 'application/json',
        'galaxy-ap-name': os.environ.get('PEOPLE_API_NAME'),
        'galaxy-ap-password': os.environ.get('PEOPLE_API_PASS'),
        'galaxy-search-type': 'DevAPIContactEnrich'
    }


    r = requests.post('https://api.peoplefinderspro.com/contact/enrich', data=payload, headers=headers)
    response_body = r.text
    # print(f'response_body: {response_body}')
    person_data = json.loads(response_body)
    # print(f'person_data: {person_data}')
    # print(f'type(person_data): {type(person_data)}')
    if not "person" in person_data.keys():
        return False
    person_data = r.json()
    # print(f'person_data: {person_data}')
    return person_data


def update_person_db(db, lead, age, mobile_phones, emails):
    # Insert all phone numbers of lead into phone numbers table
    for phone in mobile_phones:
        # print(f'phone: {phone}')
        new = Phone_Number(mobile_phone=phone, lead_id=lead.id)
        db.session.add(new)
    for email in emails:
        new = Email(email_address=email, lead_id=lead.id)
        db.session.add(new)
    if not age == '':
        lead.age = age
    lead.last_trace = datetime.utcnow()

def retrieve_selected_leads(db, lead_ids):
    tuple_selected = convert_lead_ids_to_ints(lead_ids)
    leads = db.session.query(Lead).filter(Lead.id.in_(tuple_selected)).all()
    return leads

def get_lead_dict(lead):
    lead_dict = {
        "FirstName": lead.first_name,
        "LastName": lead.last_name,
        "Address": {
            "addressLine1": lead.address,
            "addressLine2": f'{lead.city}, {lead.state}'
        }
    }
    return lead_dict
# Added by Dylan
# changed by Zack
def filter(category, query_string, rows):
    page = request.args.get("page", 1, type=int)
    leads = (
        db.session.query(Lead)
        .filter(getattr(Lead, category).like(f"%{query_string}%"))
        .paginate(page=page, per_page=rows)
    )
    return leads
