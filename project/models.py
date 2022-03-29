from datetime import datetime
from enum import unique
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

from project.__init__ import db


class BaseMixin:
    @classmethod
    def create(cls, **kw):
        """adds new item to database

        this is inherited by all SQLAlchemy classes
        """
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj

    def __repr__(self) -> str:
        repr_ = f"{self.__tablename__}("
        for column in self.__table__.columns:
            repr_ += f"{column.key}={getattr(self, str(column.key))}, "
        repr_ = repr_[:-2] + ")"

        return repr_

class Users(BaseMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True)
    hashed_password = db.Column(db.String(120), nullable=False)

    @classmethod
    def create(cls, **kw):
        """adds new User to database and hashes their password.
        it also adds the user to bug reports
        """
        kw["hashed_password"] = generate_password_hash(kw["password"], method="sha256")
        kw.pop("password")
        user = super().create(**kw)
        return user

class Lead(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    age = db.Column(db.String(30))  # just added
    address = db.Column(db.String(200))
    city = db.Column(db.String(200))
    state = db.Column(db.String(200))
    zip = db.Column(db.String(200))
    owner_occupied = db.Column(db.String)
    property_type = db.Column(db.String)
    mls_status = db.Column(db.String)
    phone_number = db.Column(db.String(200)) # can't be removed due to csv template
    email = db.Column(db.String(200)) # can't be removed due to csv template
    mobile_phones = db.relationship("Phone_Number", backref="lead")
    emails = db.relationship("Email", backref="lead")
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    trace_date = db.Column(db.DateTime)
    template_sent = db.Column(db.String(200))
    response = db.Column(db.String(2000))
    motivation_level = db.Column(db.String(200))
    last_trace = db.Column(db.DateTime)



class Phone_Number(BaseMixin, db.Model):
    __tablename__ = "phone_number"
    id = db.Column(db.Integer, primary_key=True)
    mobile_phone = db.Column(db.String(20), nullable=False, unique=True)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    response = db.relationship("TextReply", backref="phone_number")
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"))


class TextReply(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(2000), nullable=False)
    contact_time = db.Column(db.DateTime)
    phone_id = db.Column(db.Integer, db.ForeignKey("phone_number.id"))
    additional = {}


class Email(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    response = db.Column(db.String(200))
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"))



class EmailReply(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    contact_time = db.Column(db.DateTime)
    email_id = db.Column(db.Integer, db.ForeignKey("email.id"))


class Template(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(200), nullable=False)
