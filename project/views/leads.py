from datetime import datetime
from typing import Tuple
import json
import os
import requests

from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from flask_login import login_required
from flask_sqlalchemy import Pagination

from project.__init__ import db
from project.forms import LeadsForm, FilterForm, SkiptraceForm, LeadsForm
from project.helpers.db_session import db_session
from project.models import Addresses, db
from project.models import Lead

leads = Blueprint("leads", __name__)


@leads.route("/leads", methods=["POST", "GET"])
@login_required
def main():
    with db_session(autocommit=False) as sess:
        filter_form = FilterForm()
        leads_form = SkiptraceForm()
        leads_form = LeadsForm()
        leads_form.select_lead.choices = []
        leads_form.leads = []
        filter_form.comp_select.choices = [
            "address",
            "city",
            "zip",
            "owner_occupied",
            "property_type",
        ]

        if request.method == "POST":
            if filter_form.filter_submit.data:
                column = filter_form.comp_select.data
                data = filter_form.info.data
                rows = filter_form.length.data
                addresses = filter(column, data, rows)
                session["filtered"] = {"column": column, "data": data, "rows": rows}
                return render(addresses, filter_form, leads_form)
            if leads_form.skip_submit.data:
                skipped_int = 0
                success = 0
                final_msg = ""
                lead_tuples = []
                for string in leads_form.select_lead.data:
                    print(string)
                    string: str
                    string_list = string.split("_")
                    lead_id, address_id = string_list[0], string_list[1]
                    lead_tuples.append((lead_id, address_id))
                for tuple in lead_tuples:
                    lead = Lead.query.get(tuple[0])
                    #     # API call does not work without first name, OR if already have phone/emails
                    if not lead.first_name:
                        skipped_int += 1
                        final_msg += f'skipping "{lead.first_name} {lead.last_name}" due to lack of information<br>'
                        continue
                    if lead.mobile_phones or lead.emails:
                        skipped_int += 1
                        final_msg += f'skipping "{lead.first_name} {lead.last_name}" due to already having phone/email<br>'
                        continue
                    # if lead.last_trace is not None:
                    #     # TODO add option to bypass this
                    #     skipped_int += 1
                    #     final_msg += f'skipping "{lead.first_name} {lead.last_name}" due already being traced<br>'
                    #     continue
                    address = Addresses.query.get(tuple[1])
                    lead_dict = get_lead_dict(lead, address)
                    person_data = get_pf_api_data(lead_dict)
                    if person_data:
                        age, mobile_phones, emails = extract_info_from_person_data(
                            person_data
                        )
                        print(f'age: {age}')
                        print(f'mobile_phones: {mobile_phones}')
                        print(f'emails: {emails}')
                        lead.age = age
                        lead.add_phones(mobile_phones)
                        lead.add_emails(emails)
                        lead.last_trace = datetime.utcnow()
                    else:
                        final_msg += f'"{lead.first_name} {lead.last_name}" trace returned "No strong Matches<br>'
                        lead.last_trace = datetime.utcnow()
                    sess.add(lead)
                final_msg = (
                    final_msg[: -len("<br>")]
                    if final_msg != ""
                    else "all traces successful"
                )
                flash(final_msg)
                try:
                    sess.commit()
                    flash(
                        f"traced {success} leads successfully. skipped {skipped_int} traces."
                    )
                except Exception:
                    flash("There was an error inserting API data into database.")

            if leads_form.sms_submit.data:
                if leads_form.select_lead.data:
                    return redirect(url_for("apply.main", selected=json.dumps(leads_form.select_lead.data)))
                else:
                    return redirect(url_for("leads.main"))
        page = request.args.get("page", 1, type=int)
        if "filtered" in session.keys():
            addresses = filter(
                session["filtered"]["column"],
                session["filtered"]["data"],
                session["filtered"]["rows"],
            )
        else:
            addresses = (
                db.session.query(Addresses)
                .order_by(Addresses.id)
                .paginate(page=page, per_page=10)
            )
        for address in addresses.items:
            # This is where the selections from wtforms are paired with the database items
            setattr(address, "forms", [])
            address: Addresses
            for lead in address.leads:
                lead: Lead
                leads_form.select_lead.choices.append((f"{lead.id}_{address.id}"))
                # this is done this way because wtforms choices are kind of weird. 
                # I was looking for a better solution
                for choice in leads_form.select_lead:
                    pass
                address.forms.append((choice, lead))

        leads_form.select_address.choices = ["" for _ in range(addresses.per_page)]
        return render(addresses, filter_form, leads_form)


@leads.route("/leads/clear", methods=["GET"])
def clear():
    try:
        session.pop("filtered")
    except KeyError:
        pass
    return redirect(url_for("leads.main"))


def render(
    addresses: Pagination,
    filter_form: FilterForm,
    leads_form: LeadsForm,
):
    """render template function just used to be less verbose"""
    return render_template(
        "leads.html",
        addresses=addresses,
        filter_form=filter_form,
        leads_form=leads_form,
    )


def extract_info_from_person_data(person_data: dict) -> Tuple:
    """function that parses the incoming skiptrace data and returns relevant info"""
    age = (
        person_data["person"]["age"]
        if person_data["person"]["age"] != ""
        else "Unknown"
    )
    emails = [x["email"] for x in person_data["person"]["emails"]]
    # mobile_phones = [n for n in person_data["person"]["phones"]]
    mobile_phones = [n for n in _phone_data(person_data["person"]["phones"])]
        # for number in _phone_data(phone_group):
        #     mobile_phones.append(number)
    return age, mobile_phones, emails

def _phone_data(phone_data: list) -> str:
    """filter phone data and return numbers that are connected and were last reported after 2015"""
    print(f'phone_data: {phone_data}')
    for number in phone_data:
        is_mobile = number["type"] == "mobile"
        is_connected = number["isConnected"]
        is_current = int(number["lastReportedDate"].split("/")[2]) > 2015
        if is_mobile and is_connected and is_current:
            yield number["number"]

def get_pf_api_data(lead_dict: dict):
    """loads dict into http POST request and returns data"""
    payload = json.dumps(lead_dict)
    headers = {
        "Content-Type": "application/json",
        "galaxy-ap-name": os.environ.get("PEOPLE_API_NAME"),
        "galaxy-ap-password": os.environ.get("PEOPLE_API_PASS"),
        "galaxy-search-type": "DevAPIContactEnrich",
    }
    print(f'payload: {payload} || headers: {headers}')
    r = requests.post(
        "https://api.peoplefinderspro.com/contact/enrich", data=payload, headers=headers
    )
    response_body = r.text
    person_data: dict = json.loads(response_body)
    if not "person" in person_data.keys():
        return False
    person_data = r.json()
    return person_data


# def update_person_db(db, lead, age, mobile_phones, emails, session):
#     # Insert all phone numbers of lead into phone numbers table
#     for phone in mobile_phones:
#         p_exists = Phone_Number.query.filter_by(mobile_phone=phone).first()
#         if p_exists is None:
#             new = Phone_Number(mobile_phone=phone, lead_id=lead.id)
#             session.add(new)
#     for email in emails:
#         e_exists = Email.query.filter_by(email_address=email).first()
#         if e_exists is None:
#             new = Email(email_address=email, lead_id=lead.id)
#             session.add(new)
#     lead.age = age
#     lead.last_trace = datetime.utcnow()


def get_lead_dict(lead: Lead, address: Addresses ):
    """formats information for the skiptrace payload"""
    lead_dict = {
        "FirstName": lead.first_name,
        "LastName": lead.last_name,
        "Address": {
            "addressLine1": address.address,
            "addressLine2": f"{address.city}, {address.state}",
        },
    }
    return lead_dict


def filter(category: str, query_string: str, rows: int) -> Pagination:
    page = request.args.get("page", 1, type=int)
    addresses: Pagination = (
        db.session.query(Addresses)
        .filter(getattr(Addresses, category).like(f"%{query_string}%"))
        .paginate(page=page, per_page=rows)
    )
    return addresses
