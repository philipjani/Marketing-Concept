# Marketing-Concept

**Marketing concept web-app**
to launch locally make sure you have docker installed.
then all you should have to do is type "docker-compose up" from your commandline to bring it up.
type "docker-compose down" in a different terminal to stop the server. ( or you can just enter CTRL+C in the same terminal

**Files:**
- migrations
    - used by Flask Migrate to setup database
    - Flask Migrate checks migrations/versions for the python alembic files to upgrade the server at every start up
    - this is done by the "ready_db()" function in \__init__.py
    - see Flask Migrate documentation for more
- project
    - where all internal application lives
    - helpers: Helper functions
    - static: static assets (CSS, JS, and other static files)
    - templates: HTML templates
    - views: internal routes of the application
    - \__init__.py: application initializer
- .flaskenv
    - only used when running application through "Flask run"
- .gitignore
    - used to list files/folders to not upload to git
- app.py
    - entry point for docker to load application
- blob.json
    - ??? from before me
- docker-compose.yml
    - used to run docker locally
- Dockerfile
    - used by all instances of Docker
- heroku.yml
    -used to deploy to heroku
- requirements.txt
    - used to list and download dependencies
- ngrok.exe
    - used by ngrok which is used when running locally
- roadmap.txt
    - old notes
- test.db
    - ??? from before me


**TODO: Running list of things I had planned to do.**
- change to .env variables:
    - "SQLALCHEMY_DATABASE_URI"
- split text responses (Lead.response) into their own table. 
    - this will allow saving a history of responses instead of just the most recent one
- compartmentalize actions into classes/functions throughout
    - for example, make a Filter class that filters the selections from leads
- change flashed messages in file uploads/skiptraces into logs
    - detailed reports could then be emailed to you or sent to a google drive etc
- create better exceptions to isolate known errors and expose others
    - More site reliablity. Needed for robust testing
- clean up apply_templates to work with MultiCheckboxField
    currently the apply_templates route and view doeesn't best use wtforms. This would hinder testing and UX
- filter form needed to be fixed to work with current database
    the current filter form is broken since addresses was split off Lead
- manage most recent number for a lead
    - add "primary_number" to table and have that be the most recent number reported
    - currently the texts are only being sent to the first number in the Lead's mobile_phones list which isn't ideal
- redo select buttons:
    - in leads the leads in the sub tables need to be selected alongside the address they are attached to.
    - impliment js that will automatically select all leads belonging to the address when the address' checkbox is selected
    - impliment js that will automatically select address attached to lead when lead's checkbox is selected
- select headers
    -clean up UI by hiding lead sub-tables. expand them when address is clicked on
- add option to bypass last trace
    currently the user cannot skiptrace a lead twice. Add a way for the user to bypass that
- add optional automatic deletion of contacts that can't be traced
- add way to only text specific numbers of a lead.
    - currently texts all
- better format the leads table to fit screen display data more intuitively
- impliment unit testing for site reliability
- rename database classes to follow best practices (CamelCase)



**Heroku:**
Heroku currently hosts the application and is configured through the Dockerfile and heroku.yml
docker-compose.yml is just for local deployment

to upload a new release to heroku you need to log into heroku through your cli. (you first need to install the heroku cli) 
then from your cli add and commit the new release and push it up to heroku
git add .
git commit -am "message"
git push heroku main
you can download a back up of the database from the heroku app in the Postgres addon
see heroku docs for more.

**Old README:**

Real Estate Lead Generation Software

Problem: Can't find enough off-market real estate leads to generate consistent business.

Solution: Build an app that can pull property/owner info by zip code and send automated text messages to leads to see if they are willing to sell their houses.

Get/Scrape a large volume of data (10k+) as quickly as possible about homeowners (First Name, Last Name, Cell Phone Number, Email, Address) by zip code using True People Search/People Search Now or a reverse people/phone search api.

Use automated SMS software to send inquiries to homeowners about their interest in selling their home(s).

Example SMS:
Hello [First_Name]! I was interested in your home located at [Home_Address]. Would you be interested in selling your home?

Also send the same message in spanish to target Reading City zip codes.

Receive responses and record their responses in the system.

Send interested leads to Partners to follow up with.

Use the system to send drip SMS messages/nurture leads.

True People Search Information and Free SMS API (Resources):
https://github.com/thehappydinoa/TruePeopleSearch
https://github.com/typpo/textbelt
Use True People Search and https://www.peoplesearchnow.com to find owner info.
People Search now seems to be more accurate (Need to validate data either way).
https://docs.jasminsms.com/en/latest/billing/index.html (SMS Gateway)
https://peopledataapi.com/developer-api/address-autocomplete/
https://docs.textbelt.com

Things needed:
True People Search/Reverse Owner Data (Owner/Phone Number/Address etc.)
Open-Source SMS service or Twilio to send text message templates in mass
Database to store and analyze responses from leads
Design Summary

I am looking for a web app that allows me to gather all owner/property records including owner first name, last name, phone number, email and full property address(es) by entering a list of target zip codes into the system and by uploading a CSV/Excel File of target zip codes.

The system should clean, validate and store all gathered seller leads data into tables by zip code and allow me to select how many recipients I would like to send a text message blast to.

The system should allow me to create, save and name various text message templates that can be selected to send to a predetermined amount of recipients using a local (610) area code phone number.

The system should be able to send and receive text messages to/from leads and detect whether a text was sent successfully/unsuccessfully

The system should be able to receive, collect and store all responses from recipients in a "Response Column" and perform sentiment analysis on seller's response to determine motivated sellers, likelihood/willingness of the lead to sell their home, do business or receive a follow up call.

The system should allow/keep track of:
Number of leads, 
Which leads have been contacted, 
How many times each lead was contacted, 
Text message conversations, 
Response texts in app, 
Filter between contacted and uncontacted leads, 
What date and time leads were texted, 
Each lead's level of motivation to sell their house based on sentiment analysis,
Response rates based on campaign/zip code
Filter by motivation levels (Highly Motivated, Moderately Motivated, Unmotivated etc.)
Bulk remove leads that are clearly uninterested,
Successfully closed leads,
Percentage of successfully closed leads,
Store how much money was generated from a closed lead,
Store total amount of money generated from all closed leads per zip code
Status of sent messages (Successfully sent/Failed to send)
Be able to choose columns/export all motivated seller leads to excel or csv file
Should only have data of people who are age 30 and up

System/Web app requires Login functionality, GUI and hosting in the cloud.