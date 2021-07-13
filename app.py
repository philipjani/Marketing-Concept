from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(200), nullable=False)
    zip_code = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime, nullable=False)
    template_sent = db.Column(db.String(200), nullable=False)
    response = db.Column(db.String(200), nullable=False)
    motivation_level = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Lead %r>' % self.id

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)