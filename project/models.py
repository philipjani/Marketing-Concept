from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import BaseQuery
from project.__init__ import db
from sqlalchemy.orm.scoping import scoped_session


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


lead_addresses = db.Table(
    "lead_addresses",
    db.Model.metadata,
    db.Column("lead_id", db.Integer, db.ForeignKey("lead.id")),
    db.Column("address.id", db.Integer, db.ForeignKey("addresses.id")),
)


class Users(BaseMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True)
    hashed_password = db.Column(db.String(120), nullable=False)
    texts_left = db.Column(db.Integer(), default=0)

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
    id: int = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name: str = db.Column(db.String(200))
    last_name: str = db.Column(db.String(200))
    age: str = db.Column(db.String(30))  # just added
    address: str = db.Column(db.String(200))  # moving to address table
    city: str = db.Column(db.String(200))  # moving to address table
    state: str = db.Column(db.String(200))  # moving to address table
    zip: str = db.Column(db.String(200))  # moving to address table
    owner_occupied: str = db.Column(db.String)  # moving to address table
    property_type: str = db.Column(db.String)  # moving to address table
    mls_status: str = db.Column(db.String)
    phone_number: str = db.Column(
        db.String(200)
    )  # can't be removed due to csv template
    email: str = db.Column(db.String(200))  # can't be removed due to csv template
    addresses = db.relationship(
        "Addresses",
        secondary=lead_addresses,
        lazy="subquery",
        backref=db.backref("leads", lazy=True),
    )
    mobile_phones = db.relationship("Phone_Number", backref="lead")
    emails = db.relationship("Email", backref="lead")
    contacted: int = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    trace_date = db.Column(db.DateTime)
    template_sent: str = db.Column(db.String(200))
    # TODO split this off into its own table
    response: str = db.Column(db.String(2000))
    motivation_level: str = db.Column(db.String(200))
    last_trace = db.Column(db.DateTime)

    @classmethod
    def get_property_types(cls) -> list:
        L: cls
        query: BaseQuery = cls.query
        types = set()
        all = query.all()
        for L in all:
            types.add(L.property_type)
        return list(types)

    @classmethod
    def get_llcs(cls):
        query: BaseQuery = Lead.query
        all: list[Lead] = query.all()
        llcs = []
        for LLC in all:
            if LLC and LLC.first_name and "llc" in LLC.first_name.lower():
                llcs.append(LLC)
        return llcs

    @classmethod
    def delete_rows(cls, to_delete: list, session: scoped_session, autocommit=True):
        for rm in to_delete:
            session.delete(rm)
        if autocommit:
            session.commit()

    def add_emails(self, emails: list, check: bool = True):
        """add emails to lead. set check to `False` to skip database check"""
        if not emails:
            return
        for email in emails:
            if check:
                self.add_email(email)
            else:
                self.add_email_nocheck(email)

    def add_email_nocheck(self, email: str):
        """add email to lead skipping the database check"""
        print(f'email: {email}')
        if not email:
            return
        new_email = Email(email_address=email)
        self.emails.append(new_email)

    def add_email(self, email: str):
        """add email to lead"""
        print(f'email: {email}')
        print(f'self.emails: {self.emails}')
        existing_email = Email.query.filter_by(email_address=email).first()
        if existing_email:
            self.emails.append(existing_email)
            return
        self.add_email_nocheck(email)

    def add_phones(self, phone_numbers: list, check: bool = True):
        """add phone numbers to lead. set check to `False` to skip database check"""
        if not phone_numbers:
            return
        for phone in phone_numbers:
            if check:
                self.add_phone(phone)
            else:
                self.add_phone_nocheck(phone)

    def add_phone_nocheck(self, phone: str):
        """add phone number to lead skipping the database check"""
        if not phone:
            return
        standardized_number = convert_phone(phone)
        new_phone = Phone_Number(mobile_phone=standardized_number)
        self.mobile_phones.append(new_phone)


    def add_phone(self, phone: str):
        """add phone number to lead"""
        new_phone = Phone_Number.query.filter_by(mobile_phone=phone).first()
        if new_phone:
            return self.mobile_phones.append(new_phone)
        self.add_phone_nocheck(phone)

def convert_phone(phone: str):
    """used to make sure all numbers follow the same format"""
    # TODO use a library to make sure that this is bug free
    converted = ""
    for symbol in phone:
        if symbol.isnumeric():
            converted += symbol
    return converted

class Addresses(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(200))
    state = db.Column(db.String(200))
    zip = db.Column(db.String(200))
    owner_occupied = db.Column(db.String)
    property_type = db.Column(db.String)


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
