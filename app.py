from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

#https://stackoverflow.com/questions/36015756/no-such-file-or-directory-uploads
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/files')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
#https://flask-migrate.readthedocs.io/en/latest/
migrate = Migrate(app, db)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(200), nullable=False)
    zip_code = db.Column(db.String(200), nullable=False)
    owner_occupied = db.Column(db.String, nullable=False)
    property_type = db.Column(db.String, nullable=False)
    mls_status = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    template_sent = db.Column(db.String(200), nullable=False)
    response = db.Column(db.String(200), nullable=False)
    motivation_level = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Lead %r>' % self.id

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Template %r>' % self.id

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

@app.route('/leads')
def leads():
    con = sqlite3.connect('test.db')

    cur = con.cursor()
    cur.execute("SELECT * FROM lead WHERE property_type LIKE '%Residential%' LIMIT 10;")
    data = cur.fetchall()
    return render_template('leads.html', data=data)

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
            return 'There was an issue adding your template'
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


@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

@app.errorhandler(500)
def page_not_found(error):
   return render_template('500.html', title = '500'), 500

if __name__ == '__main__':
    app.run(debug=True)