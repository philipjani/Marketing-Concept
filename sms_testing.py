import requests
import os
import sqlite3

con = sqlite3.connect('test.db')
cur = con.cursor()
testing = cur.execute("select * from lead where last_name like '%jani%';")

for row in testing:
    x = row[11]

r = requests.post('https://textbelt.com/text', {
  # 'phone': f'2153171046',
  'phone': "2062933922",
  'message': 'Hello [Name], this is a test [Address][City][State][Zip].',
  'key': os.getenv('TEXTBELT_API_KEY'),
  'replyWebhookUrl': 'http://756c-2601-989-4580-8ea0-c4c5-506e-e425-fad6.ngrok.io/textreply'
})

print(r.json())

