from flask_sqlalchemy import SQLAlchemy
import requests
import sqlite3
import json
import os
from pprint import pprint

def retrieve_selected_leads():
    test_selected = ['0', '1', '3', '8']
    ints_selected = []
    for id_num in test_selected:
        ints_selected.append(int(id_num))
        tuple_selected = tuple(ints_selected)
    con = sqlite3.connect('test.db')
    cur = con.cursor()
    # cur.execute(f"SELECT * FROM lead WHERE property_type LIKE '%Residential%' AND mls_status LIKE '%FAIL%' AND id IN {tuple_selected} LIMIT 10;")
    cur.execute(f"SELECT * FROM lead WHERE id IN {tuple_selected};")
    rows = cur.fetchall()
    return rows

def contact_pf_api(rows):
    for row in rows:

        id_ = row[0]
        f_name = row[1]
        l_name = row[2]
        add_line_one = row[4]
        add_line_two = f'{row[5]}, {row[6]}'

        values = {
            "FirstName": f_name,
            "LastName": l_name,
            "Address": {
                "addressLine1": add_line_one,
                "addressLine2": add_line_two
            }
            }

        # https://stackoverflow.com/questions/20777173/add-variable-value-in-a-json-string-in-python/20777249
        values = json.dumps(values)
        
        headers = {
            'Content-Type': 'application/json',
            'galaxy-ap-name': os.environ.get('PEOPLE_API_NAME'),
            'galaxy-ap-password': os.environ.get('PEOPLE_API_PASS'),
            'galaxy-search-type': 'DevAPIContactEnrich'
        }

        r = requests.post('https://api.peoplefinderspro.com/contact/enrich', data=values, headers=headers)
        response_body = r.text
        person_data = json.loads(response_body)

        return person_data

def return_phone_and_email(person_data):
    first_name = person_data['person']['name']['firstName']
    last_name = person_data['person']['name']['lastName']
    middle_name = person_data['person']['name']['middleName']
    age = person_data['person']['age']
    email_data = person_data['person']['emails']
    emails = [x['email'] for x in email_data]
    phone_data = person_data['person']['phones']
    mobile_phones = [x['number'] for x in phone_data if x['type'] == 'mobile' and x['isConnected'] == True and int(x['lastReportedDate'].split('/')[2]) > 2015]

    return list(mobile_phones, emails)