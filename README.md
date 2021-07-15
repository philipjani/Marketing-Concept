# Marketing-Concept

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