from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, abort
# from sqlalchemy import text, create_engine
from app import Lead, Phone_Number, Email
import requests
import sqlite3
import json
import os
from pprint import pprint

app = Flask(__name__)

#https://stackoverflow.com/questions/36015756/no-such-file-or-directory-uploads
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/files')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# try sqlalchemy to join tables
# https://stackoverflow.com/questions/28105465/joining-multiple-tables-with-one-to-many-relationship
# https://stackoverflow.com/questions/11003347/multiple-table-joins-with-one-to-many-relationships
# try merge w/ pandas instead
# use python!
# https://stackoverflow.com/questions/23025902/sqlalchemy-one-to-many-relationship-join

# try:
test_selected = ['0', '1', '3', '8']
ints_selected = []
for id_num in test_selected:
    ints_selected.append(int(id_num))
tuple_selected = tuple(ints_selected)

leads = db.session.query(Lead).filter(Lead.id.in_(tuple_selected)).all()

for lead in leads:
    values = {
        "FirstName": lead.first_name,
        "LastName": lead.last_name,
        "Address": {
            "addressLine1": lead.address,
            "addressLine2": f'{lead.city}, {lead.state}'
        }
    }
    # print(values)

    # if lead.mobile_phones != [] or lead.emails != []:
    #     continue

#   # https://stackoverflow.com/questions/20777173/add-variable-value-in-a-json-string-in-python/20777249
#   values = json.dumps(values)
  
#   headers = {
#     'Content-Type': 'application/json',
#     'galaxy-ap-name': os.environ.get('PEOPLE_API_NAME'),
#     'galaxy-ap-password': os.environ.get('PEOPLE_API_PASS'),
#     'galaxy-search-type': 'DevAPIContactEnrich'
#   }

#   # r = requests.post('https://api.peoplefinderspro.com/contact/enrich', data=values, headers=headers)
#   # response_body = r.text
#   # person_data = json.loads(response_body)

    with open('blob.json') as blob:
        person_data = json.load(blob)

    first_name = person_data['person']['name']['firstName']
    last_name = person_data['person']['name']['lastName']
    middle_name = person_data['person']['name']['middleName']
    age = person_data['person']['age']
    email_data = person_data['person']['emails']
    emails = [x['email'] for x in email_data]
    phone_data = person_data['person']['phones']
    mobile_phones = [x['number'] for x in phone_data if x['type'] == 'mobile' and x['isConnected'] == True and int(x['lastReportedDate'].split('/')[2]) > 2015]

    # Insert all phone numbers of lead into phone numbers table
    for phone in mobile_phones:
        stmt = Phone_Number.__table__.insert().prefix_with('OR IGNORE').values(dict(mobile_phone=phone, lead_id=lead.id))
        db.session.execute(stmt)
  
    # Insert all email of lead into emails table
    for email in emails:
        stmt = Email.__table__.insert().prefix_with('OR IGNORE').values(dict(email_address=email, lead_id=lead.id))
        db.session.execute(stmt)

    # Update age of leads
    lead.age = age

    try:
      db.session.commit()
    
    except:
      print("There was an error inserting API data into database.")

    # numbers = db.session.query(Phone_Number).all()
    # print(numbers, 'hi')
    # for number in numbers:
    #     print(number.mobile_phone, number.lead_id)

    # emails = db.session.query(Email).all()
    # print(emails)
    # for email in emails:
    #     print(email.email_address, email.lead_id)

    # break

# except:
#   print("There was an error in fetching lead data from the API.")

