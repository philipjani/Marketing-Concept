from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os
from project.models import Lead, Phone_Number, Email, Template
from pprint import pprint


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


def get_pf_api_data(lead_dict):
    payload = json.dumps(lead_dict)
  
    headers = {
        'Content-Type': 'application/json',
        'galaxy-ap-name': os.environ.get('PEOPLE_API_NAME'),
        'galaxy-ap-password': os.environ.get('PEOPLE_API_PASS'),
        'galaxy-search-type': 'DevAPIContactEnrich'
    }

    r = requests.post('https://api.peoplefinderspro.com/contact/enrich', data=payload, headers=headers)
    # response_body = r.text
    # person_data = json.loads(response_body)
    person_data = r.json()
    return person_data


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

# def contact_pf_api(db, leads):
#     leads = retrieve_selected_leads(db, lead_ids)
#     for lead in leads:
#         lead_dict = get_lead_dict(lead)
#         person_data = get_pf_api_data(lead_dict)
#         age, mobile_phones, emails = extract_info_from_person_data(person_data)
#         update_person_db(db, age, mobile_phones, emails)