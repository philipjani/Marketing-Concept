import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash
import json
import os
import requests
from project.__init__ import db
from project.forms import FilterForm, LeadForm
from project.models import db
from project import skiptracing as st
from project.models import Lead, Phone_Number, Email

leads = Blueprint("leads", __name__)


@leads.route("/leads", methods=["POST", "GET"])
def main():

    filter_form = FilterForm()
    lead_form = LeadForm()
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
        
        if filter_form.filter_submit.data:
            column = filter_form.comp_select.data
            data = filter_form.info.data
            rows = filter_form.length.data
            leads_ = filter(column, data, rows)
        if lead_form.lead_submit.data:
            leads_ = retrieve_selected_leads(db, selected)
            
            for lead in leads_:
            #     # API call does not work without first name, OR if already have phone/emails
                if not lead.first_name or lead.mobile_phones or lead.emails:
            #         # print('Skipped!')
                    continue
                lead_dict = get_lead_dict(lead)
                print(f'lead_dict: {lead_dict}')
            #     # pprint(lead_dict)
                person_data = get_pf_api_data(lead_dict)
            # #     # pprint(person_data)
                age, mobile_phones, emails = extract_info_from_person_data(person_data)
                update_person_db(db, lead, age, mobile_phones, emails)
    if request.method == "GET":
        page = request.args.get("page", 1, type=int)
        leads_ = db.session.query(Lead).paginate(page=page, per_page=20)
    return render_template(
        "leads.html", lead_form=lead_form, leads=leads_, filter_form=filter_form
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
    age = person_data['person']['age']
    email_data = person_data['person']['emails']
    emails = [x['email'] for x in email_data]
    phone_data = person_data['person']['phones']
    mobile_phones = [x['number'] for x in phone_data if x['type'] == 'mobile' and x['isConnected'] == True and int(x['lastReportedDate'].split('/')[2]) > 2015]
    return age, mobile_phones, emails

def get_pf_api_data(lead_dict):
    payload = json.dumps(lead_dict)
    print(f'payload: {payload}')
    headers = {
        'Content-Type': 'application/json',
        'galaxy-ap-name': os.environ.get('PEOPLE_API_NAME'),
        'galaxy-ap-password': os.environ.get('PEOPLE_API_PASS'),
        'galaxy-search-type': 'DevAPIContactEnrich'
    }

    # r = requests.post('https://api.peoplefinderspro.com/contact/enrich', data=payload, headers=headers)
    # response_body = r.text
    # person_data = json.loads(response_body)
    # person_data = r.json()
    # return person_data

def update_person_db(db, lead, age, mobile_phones, emails):
    # Insert all phone numbers of lead into phone numbers table
    for phone in mobile_phones:
        stmt = Phone_Number.__table__.insert().prefix_with('OR REPLACE').values(dict(mobile_phone=phone, lead_id=lead.id))
        db.session.execute(stmt)
  
    # Insert all email of lead into emails table
    for email in emails:
        stmt = Email.__table__.insert().prefix_with('OR REPLACE').values(dict(email_address=email, lead_id=lead.id))
        db.session.execute(stmt)

    # Update age of leads
    lead.age = age

    try:
      db.session.commit()
    
    except:
      print("There was an error inserting API data into database.")

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
