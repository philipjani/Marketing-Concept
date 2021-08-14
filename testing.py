import requests
import json
import os

try:
  con = sqlite3.connect('test.db')
  cur = con.cursor()
  cur.execute("SELECT * FROM lead WHERE property_type LIKE '%Residential%' AND mls_status LIKE '%FAIL%' LIMIT 10;")
  data = cur.fetchall()

  for i in range(len(data)):
    id_ = data[i][0]
    f_name = data[i][1]
    l_name = data[i][2]
    add_line_one = data[i][4]
    add_line_two = f'{data[i][5]}, {data[i][6]}'

    values = """
      {
        "FirstName": f'{f_name}',
        "LastName": f'{l_name}',
        "Address": {
          "addressLine1": f'{add_line_one}',
          "addressLine2": f'{add_line_two}'
        }
      }
    """

    headers = {
      'Content-Type': 'application/json',
      'galaxy-ap-name': os.environ.get('PEOPLE_API_NAME'),
      'galaxy-ap-password': os.environ.get('PEOPLE_API_PASS'),
      'galaxy-search-type': 'DevAPIContactEnrich'
    }

    r = requests.post('https://api.peoplefinderspro.com/contact/enrich', data=values, headers=headers)
    response_body = r.text

    person_data = json.loads(response_body)
    age = person_data['person']['age']
    email_data = person_data['person']['emails']
    emails = [x['email'] for x in email_data]
    phone_data = person_data['person']['phones']
    mobile_phones = [x['number'] for x in phone_data if x['type'] == 'mobile' and x['isConnected'] == True]

    try:
      cur.execute("INSERT INTO lead (age) VALUES (?)", age)
      cur.execute("INSERT INTO phone_number (lead_id) VALUES (?)", id)
      cur.execute("INSERT INTO email (lead_id) VALUES (?)", id)
      cur.executemany("INSERT INTO phone_number VALUES (?,?,?,?,?,?)", mobile_phones)
      cur.executemany("INSERT INTO email VALUES (?,?,?,?,?,?)", emails)
    except:
      return "There was an error inserting API data into database."
except:
  return "There was an error in fetching lead data from the API."