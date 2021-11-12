from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import text, create_engine
import requests
import sqlite3
import json
import os
from pprint import pprint

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

con = sqlite3.connect('test.db')
cur = con.cursor()

# cur.execute(f"SELECT * FROM lead WHERE property_type LIKE '%Residential%' AND mls_status LIKE '%FAIL%' AND id IN {tuple_selected} LIMIT 10;")
cur.execute(f"SELECT * FROM lead WHERE id IN {tuple_selected};")
rows = cur.fetchall()

for row in rows:
  # print(row)
  id_ = row[0]
  f_name = row[1]
  l_name = row[2]
  add_line_one = row[4]
  add_line_two = f'{row[5]}, {row[6]}'

  # if row[11] or row[12]:
  #   continue


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

  # r = requests.post('https://api.peoplefinderspro.com/contact/enrich', data=values, headers=headers)
  # response_body = r.text
  # person_data = json.loads(response_body)

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

  l_id = id_

  # for phone in mobile_phones:
  #   cur.execute("INSERT OR IGNORE INTO phone__number (mobile_phone, lead_id) VALUES (?, ?)", (phone, l_id))

  # for email in emails:
  #   cur.execute("INSERT OR IGNORE INTO email (email, lead_id) VALUES (?, ?)", (email, l_id))
  # con.commit()

  cur.execute(f"SELECT * FROM email;")


  # cur.execute(f"""SELECT * FROM lead L
  #                 INNER JOIN phone__number P
  #                 ON L.id = P.lead_id
  #                 WHERE L.id IN {tuple_selected};
  #                 """)



  # cur.execute(f"""SELECT
  #                   L.id, 
  #                   L.first_name,
  #                   L.last_name,
  #                   L.age,
  #                   L.address,
  #                   L.city,
  #                   L.state,
  #                   L.zip,
  #                   L.owner_occupied,
  #                   L.property_type,
  #                   L.mls_status,
  #                   group_concat(P.mobile_phone),
  #                   group_concat(E.email),
  #                   L.contacted,
  #                   L.contact_time,
  #                   L.template_sent,
  #                   L.response,
  #                   L.motivation_level
  #                  FROM lead L
  #                 INNER JOIN phone__number P ON L.id = P.lead_id
  #                 INNER JOIN Email E on L.id = E.lead_id
  #                 WHERE L.id IN {tuple_selected}
  #                 """)


  # cur.execute(f"""SELECT DISTINCT
  #                 L.id, 
  #                 L.first_name,
  #                 L.last_name,
  #                 L.age,
  #                 L.address,
  #                 L.city,
  #                 L.state,
  #                 L.zip,
  #                 L.owner_occupied,
  #                 L.property_type,
  #                 L.mls_status,
  #                 P.mobile_phone,
  #                 E.email,
  #                 L.contacted,
  #                 L.contact_time,
  #                 L.template_sent,
  #                 L.response,
  #                 L.motivation_level
  #                 FROM lead L
  #                 INNER JOIN phone__number P ON L.id = P.lead_id
  #                 INNER JOIN Email E on L.id = E.lead_id
  #               WHERE L.id IN {tuple_selected}
  #               """)


  # cur.execute(f"""SELECT group_concat(mobile_phone) FROM (SELECT DISTINCT
  #                 L.id, 
  #                 L.first_name,
  #                 L.last_name,
  #                 L.age,
  #                 L.address,
  #                 L.city,
  #                 L.state,
  #                 L.zip,
  #                 L.owner_occupied,
  #                 L.property_type,
  #                 L.mls_status,
  #                 P.mobile_phone,
  #                 E.email,
  #                 L.contacted,
  #                 L.contact_time,
  #                 L.template_sent,
  #                 L.response,
  #                 L.motivation_level
  #                 FROM lead L
  #                 INNER JOIN phone__number P ON L.id = P.lead_id
  #                 INNER JOIN Email E on L.id = E.lead_id
  #               WHERE L.id IN {tuple_selected})
  #               """)


  # cur.execute(f"""SELECT  group_concat(S.mobile_phone)
  #           FROM lead L INNER JOIN (SELECT DISTINCT P.mobile_phone
  #                 FROM lead L
  #                 INNER JOIN phone__number P ON L.id = P.lead_id
  #               ) S
  #               WHERE L.id IN {tuple_selected};
  #               """)

  cur.execute(f"""SELECT 
                  P.id, 
                  P.first_name,
                  P.last_name,
                  P.age,
                  P.address,
                  P.city,
                  P.state,
                  P.zip,
                  P.owner_occupied,
                  P.property_type,
                  P.mls_status,
                  group_concat(P.mobile_phone),
                  group_concat(E.email),
                  P.contacted,
                  P.contact_time,
                  P.template_sent,
                  P.response,
                  P.motivation_level
                  FROM (SELECT DISTINCT
                    L.id, 
                    L.first_name,
                    L.last_name,
                    L.age,
                    L.address,
                    L.city,
                    L.state,
                    L.zip,
                    L.owner_occupied,
                    L.property_type,
                    L.mls_status,
                    P.mobile_phone,
                    L.contacted,
                    L.contact_time,
                    L.template_sent,
                    L.response,
                    L.motivation_level
                  FROM lead L
                  INNER JOIN phone__number P ON L.id = P.lead_id
                  WHERE L.id IN {tuple_selected}
                ) P
                  INNER JOIN (SELECT DISTINCT E.lead_id, E.email
                  FROM lead L
                  INNER JOIN Email E ON L.id = E.lead_id
                  WHERE L.id IN {tuple_selected}
                ) E;
                """)


  cur.execute(f"""SELECT 
                  group_concat(P.mobile_phone)
                  FROM (SELECT DISTINCT
                    L.id, 
                    L.first_name,
                    L.last_name,
                    L.age,
                    L.address,
                    L.city,
                    L.state,
                    L.zip,
                    L.owner_occupied,
                    L.property_type,
                    L.mls_status,
                    P.mobile_phone,
                    L.contacted,
                    L.contact_time,
                    L.template_sent,
                    L.response,
                    L.motivation_level
                  FROM lead L
                  INNER JOIN phone__number P ON L.id = P.lead_id
                  WHERE L.id IN {tuple_selected}
                ) P
                  INNER JOIN (SELECT DISTINCT E.lead_id, E.email
                  FROM lead L
                  INNER JOIN Email E ON L.id = E.lead_id
                  WHERE L.id IN {tuple_selected}
                ) E ON P.id = E.lead_id;
                """)

  rows = cur.fetchall()
  print(rows)
  print(len(rows))



  break
  # print(mobile_phones)
  # print('\n'.join(mobile_phones))

    # try:
  cur.execute("UPDATE lead SET age = ? WHERE last_name = ? AND (first_name = ? OR first_name = ?)", (age, last_name, middle_name, first_name)) #changed

  # #Create SQLAlchemy connection and query for user that was just updated to get the id
  # engine = create_engine('sqlite:///test.db')
  # t = text("SELECT * from lead WHERE last_name=:last_name AND (first_name=:middle_name OR first_name=:first_name)")
  # connection = engine.connect()
  # results = connection.execute(t, last_name=last_name, middle_name=middle_name, first_name=first_name)
  # l_id = results.fetchone()[0]
  # connection.close()


    # except:
    #   print("There was an error inserting API data into database.")
# except:
#   print("There was an error in fetching lead data from the API.")

