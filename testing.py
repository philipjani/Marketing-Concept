from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine
import requests
import sqlite3
import json
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine
import sqlite3


# try:
con = sqlite3.connect('test.db')
cur = con.cursor()
cur.execute("SELECT * FROM lead WHERE property_type LIKE '%Residential%' AND mls_status LIKE '%FAIL%' LIMIT 10;")
data = cur.fetchall()

for i in range(len(data)):
  print(data[i])
  id_ = data[i][0]
  f_name = data[i][1]
  l_name = data[i][2]
  add_line_one = data[i][4]
  add_line_two = f'{data[i][5]}, {data[i][6]}'

  # if data[i][11] or data[i][12]:
  #   continue
  #philipjani@yahoo.com
  #214 403 0135


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

  first_name = person_data['person']['name']['firstName']
  last_name = person_data['person']['name']['lastName']
  middle_name = person_data['person']['name']['middleName']
  age = person_data['person']['age']
  email_data = person_data['person']['emails']
  emails = [x['email'] for x in email_data]
  phone_data = person_data['person']['phones']
  mobile_phones = [x['number'] for x in phone_data if x['type'] == 'mobile' and x['isConnected'] == True]


    # try:
  cur.execute("UPDATE lead SET age = ? WHERE last_name = ? AND (first_name = ? OR first_name = ?)", (age, last_name, middle_name, first_name)) #changed

  #Create SQLAlchemy connection and query for user that was just updated to get the id
  engine = create_engine('sqlite:///test.db')
  t = text("SELECT * from lead WHERE last_name=:last_name AND (first_name=:middle_name OR first_name=:first_name)")
  connection = engine.connect()
  results = connection.execute(t, last_name=last_name, middle_name=middle_name, first_name=first_name)
  l_id = results.fetchone()[0]
  connection.close()

  for phone in mobile_phones:
    cur.execute("INSERT INTO phone__number (mobile_phone, lead_id) VALUES (?, ?)", (phone, l_id))

  for email in emails:
    cur.execute("INSERT INTO email (email, lead_id) VALUES (?, ?)", (email, l_id))
  con.commit()
    # except:
    #   print("There was an error inserting API data into database.")
# except:
#   print("There was an error in fetching lead data from the API.")

