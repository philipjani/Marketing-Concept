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


    for phone in mobile_phones:
        # db.session.add(Phone_Number(mobile_phone=phone, lead_id=lead.id))
        Phone_Number.__table__.insert().prefix_with(' IGNORE').values(dict(mobile_phone=phone, lead_id=lead.id))
    #     # cur.execute("INSERT OR IGNORE INTO phone__number (mobile_phone, lead_id) VALUES (?, ?)", (phone, l_id))
    
    # print(emails)
    for email in emails:
        stuff = dict(email=email, lead_id=lead.id)
        # print(stuff)
        Email.__table__.insert().prefix_with(' IGNORE').values(dict(email=email, lead_id=lead.id))
    #     cur.execute("INSERT OR IGNORE INTO email (email, lead_id) VALUES (?, ?)", (email, l_id))

    db.session.commit()
    # # con.commit()

    numbers = db.session.query(Phone_Number).all()
    print(numbers, 'hi')
    for number in numbers:
        print(number.mobile_phone, number.lead_id)

    emails = db.session.query(Email).all()
    print(emails)
    for email in emails:
        print(email.email_address, email.lead_id)

    # con = sqlite3.connect('test.db')
    # cur = con.cursor()
    # cur.execute(f"SELECT * FROM email;")
    # rows = cur.fetchall()
    # print(rows)
    # print(len(rows))
    break


#   # cur.execute(f"""SELECT * FROM lead L
#   #                 INNER JOIN phone__number P
#   #                 ON L.id = P.lead_id
#   #                 WHERE L.id IN {tuple_selected};
#   #                 """)



#   # cur.execute(f"""SELECT
#   #                   L.id, 
#   #                   L.first_name,
#   #                   L.last_name,
#   #                   L.age,
#   #                   L.address,
#   #                   L.city,
#   #                   L.state,
#   #                   L.zip,
#   #                   L.owner_occupied,
#   #                   L.property_type,
#   #                   L.mls_status,
#   #                   group_concat(P.mobile_phone),
#   #                   group_concat(E.email),
#   #                   L.contacted,
#   #                   L.contact_time,
#   #                   L.template_sent,
#   #                   L.response,
#   #                   L.motivation_level
#   #                  FROM lead L
#   #                 INNER JOIN phone__number P ON L.id = P.lead_id
#   #                 INNER JOIN Email E on L.id = E.lead_id
#   #                 WHERE L.id IN {tuple_selected}
#   #                 """)


#   # cur.execute(f"""SELECT DISTINCT
#   #                 L.id, 
#   #                 L.first_name,
#   #                 L.last_name,
#   #                 L.age,
#   #                 L.address,
#   #                 L.city,
#   #                 L.state,
#   #                 L.zip,
#   #                 L.owner_occupied,
#   #                 L.property_type,
#   #                 L.mls_status,
#   #                 P.mobile_phone,
#   #                 E.email,
#   #                 L.contacted,
#   #                 L.contact_time,
#   #                 L.template_sent,
#   #                 L.response,
#   #                 L.motivation_level
#   #                 FROM lead L
#   #                 INNER JOIN phone__number P ON L.id = P.lead_id
#   #                 INNER JOIN Email E on L.id = E.lead_id
#   #               WHERE L.id IN {tuple_selected}
#   #               """)


#   # cur.execute(f"""SELECT group_concat(mobile_phone) FROM (SELECT DISTINCT
#   #                 L.id, 
#   #                 L.first_name,
#   #                 L.last_name,
#   #                 L.age,
#   #                 L.address,
#   #                 L.city,
#   #                 L.state,
#   #                 L.zip,
#   #                 L.owner_occupied,
#   #                 L.property_type,
#   #                 L.mls_status,
#   #                 P.mobile_phone,
#   #                 E.email,
#   #                 L.contacted,
#   #                 L.contact_time,
#   #                 L.template_sent,
#   #                 L.response,
#   #                 L.motivation_level
#   #                 FROM lead L
#   #                 INNER JOIN phone__number P ON L.id = P.lead_id
#   #                 INNER JOIN Email E on L.id = E.lead_id
#   #               WHERE L.id IN {tuple_selected})
#   #               """)


#   # cur.execute(f"""SELECT  group_concat(S.mobile_phone)
#   #           FROM lead L INNER JOIN (SELECT DISTINCT P.mobile_phone
#   #                 FROM lead L
#   #                 INNER JOIN phone__number P ON L.id = P.lead_id
#   #               ) S
#   #               WHERE L.id IN {tuple_selected};
#   #               """)

#   # cur.execute(f"""SELECT 
#   #                 P.id, 
#   #                 P.first_name,
#   #                 P.last_name,
#   #                 P.age,
#   #                 P.address,
#   #                 P.city,
#   #                 P.state,
#   #                 P.zip,
#   #                 P.owner_occupied,
#   #                 P.property_type,
#   #                 P.mls_status,
#   #                 group_concat(P.mobile_phone),
#   #                 group_concat(E.email),
#   #                 P.contacted,
#   #                 P.contact_time,
#   #                 P.template_sent,
#   #                 P.response,
#   #                 P.motivation_level
#   #                 FROM (SELECT DISTINCT
#   #                   L.id, 
#   #                   L.first_name,
#   #                   L.last_name,
#   #                   L.age,
#   #                   L.address,
#   #                   L.city,
#   #                   L.state,
#   #                   L.zip,
#   #                   L.owner_occupied,
#   #                   L.property_type,
#   #                   L.mls_status,
#   #                   P.mobile_phone,
#   #                   L.contacted,
#   #                   L.contact_time,
#   #                   L.template_sent,
#   #                   L.response,
#   #                   L.motivation_level
#   #                 FROM lead L
#   #                 INNER JOIN phone__number P ON L.id = P.lead_id
#   #                 WHERE L.id IN {tuple_selected}
#   #               ) P
#   #                 INNER JOIN (SELECT DISTINCT E.lead_id, E.email
#   #                 FROM lead L
#   #                 INNER JOIN Email E ON L.id = E.lead_id
#   #                 WHERE L.id IN {tuple_selected}
#   #               ) E;
#   #               """)


#   # cur.execute(f"""SELECT 
#   #                 group_concat(P.mobile_phone)
#   #                 FROM (SELECT DISTINCT
#   #                   L.id, 
#   #                   L.first_name,
#   #                   L.last_name,
#   #                   L.age,
#   #                   L.address,
#   #                   L.city,
#   #                   L.state,
#   #                   L.zip,
#   #                   L.owner_occupied,
#   #                   L.property_type,
#   #                   L.mls_status,
#   #                   P.mobile_phone,
#   #                   L.contacted,
#   #                   L.contact_time,
#   #                   L.template_sent,
#   #                   L.response,
#   #                   L.motivation_level
#   #                 FROM lead L
#   #                 INNER JOIN phone__number P ON L.id = P.lead_id
#   #                 WHERE L.id IN {tuple_selected}
#   #               ) P
#   #                 INNER JOIN (SELECT DISTINCT E.lead_id, E.email
#   #                 FROM lead L
#   #                 INNER JOIN Email E ON L.id = E.lead_id
#   #                 WHERE L.id IN {tuple_selected}
#   #               ) E ON P.id = E.lead_id;
#   #               """)

#   rows = cur.fetchall()
#   print(rows)
#   print(len(rows))



#   break
#   # print(mobile_phones)
#   # print('\n'.join(mobile_phones))

#     # try:
#   cur.execute("UPDATE lead SET age = ? WHERE last_name = ? AND (first_name = ? OR first_name = ?)", (age, last_name, middle_name, first_name)) #changed

#   # #Create SQLAlchemy connection and query for user that was just updated to get the id
#   # engine = create_engine('sqlite:///test.db')
#   # t = text("SELECT * from lead WHERE last_name=:last_name AND (first_name=:middle_name OR first_name=:first_name)")
#   # connection = engine.connect()
#   # results = connection.execute(t, last_name=last_name, middle_name=middle_name, first_name=first_name)
#   # l_id = results.fetchone()[0]
#   # connection.close()


#     # except:
#     #   print("There was an error inserting API data into database.")
# # except:
# #   print("There was an error in fetching lead data from the API.")

