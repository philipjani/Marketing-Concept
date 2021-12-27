import os

import sqlite3
import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, abort

from project.models import db
from project import skiptracing as st
from project.models import Lead, Template, TextReply

main = Blueprint("main", __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #https://medevel.com/flask-tutorial-upload-csv-file-and-insert-rows-into-the-database/
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(main.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)
            #https://stackoverflow.com/questions/41900593/csv-into-sqlite-table-python
            df = pd.read_csv(UPLOAD_FOLDER + '/' + uploaded_file.filename)
            df.columns = df.columns.str.strip()
            # print(df)
            df.index.names = ['id']
            con = sqlite3.connect("test.db")
            #https://stackoverflow.com/questions/3548673/how-can-i-replace-or-strip-an-extension-from-a-filename-in-python
            # filename = os.path.splitext(uploaded_file.filename)
            # filename = filename[0]
            # df.to_sql(filename, con)
            df.to_sql('lead', con, if_exists='replace')
            con.close()
        return redirect(url_for('index'))
    else:
        return render_template('index.html')

@main.route('/leads', methods=['POST', 'GET'])
def leads():
    # add this
    # https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms
    # https://stackoverflow.com/questions/58122969/flask-multiple-forms-on-the-same-page
    # https://stackoverflow.com/questions/53134216/multiple-forms-on-1-page-python-flask
    if request.method == 'POST':
        selected = request.form.getlist('select')
        leads = st.retrieve_selected_leads(db, selected)
        for lead in leads:
            # API call does not work without first name, OR if already have phone/emails
            if not lead.first_name or lead.mobile_phones or lead.emails:
                # print('Skipped!')
                continue
            lead_dict = st.get_lead_dict(lead)
            # pprint(lead_dict)
            person_data = st.get_pf_api_data(lead_dict)
            # pprint(person_data)
            age, mobile_phones, emails = st.extract_info_from_person_data(person_data)
            st.update_person_db(db, lead, age, mobile_phones, emails)
    # try:
    page = request.args.get('page', 1, type=int)
    leads = db.session.query(Lead).paginate(page=page, per_page=ROWS_PER_PAGE)
    return render_template('leads.html', leads=leads)
    # except:
    #     return 'There was an issue retrieving your leads.'

#Added by Dylan
def filter(category, query_string):
    page = request.args.get('page', 1, type=int)
    leads = db.session.query(Lead).filter(getattr(Lead, category).like(f'%{query_string}%')).paginate(page=page, per_page=ROWS_PER_PAGE)
    return leads

#Added by Dylan
@main.route('/updated_filter', methods = ["POST", "GET"])
def updated_filter():
    if request.method == 'POST':
        column = request.form.get("comp_select")
        data = request.form.get("info")
        leads = filter(column, data)
        return render_template('leads.html', leads=leads)


@main.route('/templates', methods = ["POST", "GET"])
def templates():
    if request.method == 'POST':
        temp_name = request.form['name']
        temp_message = request.form['message']
        sms = Template(name=temp_name, message=temp_message)
        try:
            db.session.add(sms)
            db.session.commit()
            return redirect('/templates')
        except:
            return 'There was an issue adding your template.'
    else:
        #https://stackoverflow.com/questions/2633218/how-can-i-select-all-rows-with-sqlalchemy/26217436
        sms_templates = Template.query.all()
        return render_template('templates.html', sms_templates=sms_templates)

@main.route('/delete/<int:id>')
def delete(id):
    sms_to_delete = Template.query.get_or_404(id)

    try:
        #https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
        db.session.delete(sms_to_delete)
        db.session.commit()
        return redirect('/templates')
    except:
        return 'There was an error in deleting the template.'

@main.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    template_update = Template.query.get_or_404(id)
    
    if request.method == 'POST':
        template_update.name = request.form['name']
        template_update.message = request.form['message']

        try:
            db.session.commit()
            return redirect('/templates')
        except:
            return 'There was an error editing the template.'
    else:
        return render_template('update.html', template_update=template_update)

@main.route('/admin', methods=['GET'])
def admin():
    replies = TextReply.query.all()
    return render_template('admin.html', replies=replies)


@main.route('/textreply', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        reply = request.json
        print(f'dir(reply): {dir(reply)}')
        message = reply['text']
        number = reply['fromNumber']
        # try:
        #     contact_time = reply['contactTime']
        # except BaseException:
        #     contact_time = datetime.utcnow()
        TextReply.create(message=message, phone_id=number)
        return f'{request.json}', 200
    else:
        abort(400)

@main.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

@main.errorhandler(500)
def page_not_found(error):
   return render_template('500.html', title = '500'), 500