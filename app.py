from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
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
            # df.to_sql('filename', con)
            df.to_sql('lead', con, if_exists='replace')
            con.close()
        return redirect(url_for('index'))
    else:
        return render_template('index.html')

@app.route('/test')
def test():
    con = sqlite3.connect('test.db')

    cur = con.cursor()
    cur.execute("SELECT * FROM lead LIMIT 15;")
    data = cur.fetchall()
    return render_template('test.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)