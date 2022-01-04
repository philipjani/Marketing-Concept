import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash

from project.forms import FilterForm
from project.models import db
from project import skiptracing as st
from project.models import Lead, Template, TextReply

leads = Blueprint("leads", __name__)

@leads.route("/leads", methods=["POST", "GET"])
def main():
    # add this
    # https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms
    # https://stackoverflow.com/questions/58122969/flask-multiple-forms-on-the-same-page
    # https://stackoverflow.com/questions/53134216/multiple-forms-on-1-page-python-flask
    form = FilterForm()
    form.comp_select.choices = [
        "last_name",
        "city",
        "zip",
        "owner_occupied",
        "property_type",
        "mls_status",
    ]
    if request.method == "POST":
        if form.filter_submit.data:
            column = form.comp_select.data
            data = form.info.data
            rows = form.length.data
            leads_ = filter(column, data, rows)
            return render_template("leads.html", leads=leads_, form=form)

            selected = form.comp_select.data
            leads_ = retrieve_selected_leads(db, selected)
            # for lead in leads_:
            #     # API call does not work without first name, OR if already have phone/emails
            #     if not lead.first_name or lead.mobile_phones or lead.emails:
            #         # print('Skipped!')
            #         continue
            #     lead_dict = st.get_lead_dict(lead)
            #     # pprint(lead_dict)
            #     person_data = st.get_pf_api_data(lead_dict)
            #     # pprint(person_data)
            #     age, mobile_phones, emails = st.extract_info_from_person_data(person_data)
            #     st.update_person_db(db, lead, age, mobile_phones, emails)
    page = request.args.get("page", 1, type=int)
    lead_returns = db.session.query(Lead).paginate(page=page, per_page=20)
    return render_template("leads.html", leads=lead_returns, form=form)
    # except:
    #     return 'There was an issue retrieving your leads.'

def convert_lead_ids_to_ints(lead_ids):
    ints_selected = []
    for id_num in lead_ids:
        ints_selected.append(int(id_num))
    tuple_selected = tuple(ints_selected)
    return tuple_selected


def retrieve_selected_leads(db, lead_ids):
    tuple_selected = convert_lead_ids_to_ints(lead_ids)
    leads = db.session.query(Lead).filter(Lead.id.in_(tuple_selected)).all()
    return leads

# Added by Dylan
# changed by Zack
def filter(category, query_string, rows):
    page = request.args.get("page", 1, type=int)
    leads = (
        db.session.query(Lead)
        .filter(getattr(Lead, category).like(f"%{query_string}%"))
        .paginate(page=page, per_page=rows)
    )
    return leads



