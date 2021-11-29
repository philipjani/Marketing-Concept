from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import skiptracing as st
import sqlite3
import pandas as pd
import os
from pprint import pprint

app = Flask(__name__)

#https://stackoverflow.com/questions/36015756/no-such-file-or-directory-uploads
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/files')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
ROWS_PER_PAGE = 20

# https://stackoverflow.com/questions/17768940/target-database-is-not-up-to-date/17776558
# For data base migration issues: try running below commands in powershell terminal
# $ flask db init
# $ flask db stamp head
# $ flask db migrate
# $ flask db upgrade

#https://flask-migrate.readthedocs.io/en/latest/
migrate = Migrate(app, db)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, default=0) #just added
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(200), nullable=False)
    zip = db.Column(db.String(200), nullable=False)
    owner_occupied = db.Column(db.String, nullable=False)
    property_type = db.Column(db.String, nullable=False)
    mls_status = db.Column(db.String, nullable=False)
    # phone_number = db.Column(db.String(200), nullable=False)
    # email = db.Column(db.String(200), nullable=False)
    mobile_phones = db.relationship('Phone_Number', backref='lead')
    emails = db.relationship('Email', backref='lead')
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    template_sent = db.Column(db.String(200), nullable=False)
    response = db.Column(db.String(200))
    motivation_level = db.Column(db.String(200), nullable=False)


    def __repr__(self):
        return f'<Lead: {self.id}>'


class Phone_Number(db.Model):
    __tablename__ = 'phone_number'
    id = db.Column(db.Integer, primary_key=True)
    mobile_phone = db.Column(db.String(20), nullable=False)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    response = db.relationship('TextReply', backref='phone_number')
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'))
    __table_args__ = (
        db.UniqueConstraint('lead_id', 'mobile_phone', name='unique_phone_numbers'),
    )

    def __repr__(self):
        return f'<Phone_Number: {self.id}>'


class TextReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    contact_time = db.Column(db.DateTime)
    phone_id = db.Column(db.Integer, db.ForeignKey('phone_number.id'))

    def __repr__(self):
        return f'<TextReply: {self.id}>'


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(20), nullable=False)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    response = db.Column(db.String(200))
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'))
    __table_args__ = (
        db.UniqueConstraint('lead_id', 'email_address', name='unique_emails'),
    )

    def __repr__(self):
        return f'<Email: {self.id}>'


class EmailReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    contact_time = db.Column(db.DateTime)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'))

    def __repr__(self):
        return f'<EmailReply: {self.id}>'


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Template: {self.id}>'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #https://medevel.com/flask-tutorial-upload-csv-file-and-insert-rows-into-the-database/
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
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

@app.route('/leads', methods=['POST', 'GET'])
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
@app.route('/updated_filter', methods = ["POST", "GET"])
def updated_filter():
    if request.method == 'POST':
        column = request.form.get("comp_select")
        data = request.form.get("info")
        leads = filter(column, data)
        return render_template('leads.html', leads=leads)


@app.route('/templates', methods = ["POST", "GET"])
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

@app.route('/delete/<int:id>')
def delete(id):
    sms_to_delete = Template.query.get_or_404(id)

    try:
        #https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
        db.session.delete(sms_to_delete)
        db.session.commit()
        return redirect('/templates')
    except:
        return 'There was an error in deleting the template.'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
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

@app.route('/textreply', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        reply = request.json
        message = reply['text']
        number = reply['fromNumber']

        return f'{request.json}', 200
    else:
        abort(400)


@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

@app.errorhandler(500)
def page_not_found(error):
   return render_template('500.html', title = '500'), 500

if __name__ == '__main__':
    app.run(debug=True)