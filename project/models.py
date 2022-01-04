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


class Lead(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    age = db.Column(db.Integer)  # just added
    address = db.Column(db.String(200))
    city = db.Column(db.String(200))
    state = db.Column(db.String(200))
    zip = db.Column(db.String(200))
    owner_occupied = db.Column(db.String)
    property_type = db.Column(db.String)
    mls_status = db.Column(db.String)
    phone_number = db.Column(db.String(200))
    email = db.Column(db.String(200))
    mobile_phones = db.relationship("Phone_Number", backref="lead")
    emails = db.relationship("Email", backref="lead")
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    trace_date = db.Column(db.DateTime)
    template_sent = db.Column(db.String(200))
    response = db.Column(db.String(2000))
    motivation_level = db.Column(db.String(200))


class Phone_Number(BaseMixin, db.Model):
    __tablename__ = "phone_number"
    id = db.Column(db.Integer, primary_key=True)
    mobile_phone = db.Column(db.String(20), nullable=False)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    response = db.relationship("TextReply", backref="phone_number")
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"))
    __table_args__ = (
        db.UniqueConstraint("lead_id", "mobile_phone", name="unique_phone_numbers"),
    )


class TextReply(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(2000), nullable=False)
    contact_time = db.Column(db.DateTime)
    phone_id = db.Column(db.Integer, db.ForeignKey("phone_number.id"))


class Email(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(20), nullable=False)
    contacted = db.Column(db.Integer, default=0)
    contact_time = db.Column(db.DateTime)
    response = db.Column(db.String(200))
    lead_id = db.Column(db.Integer, db.ForeignKey("lead.id"))
    __table_args__ = (
        db.UniqueConstraint("lead_id", "email_address", name="unique_emails"),
    )


class EmailReply(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    contact_time = db.Column(db.DateTime)
    email_id = db.Column(db.Integer, db.ForeignKey("email.id"))


class Template(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(200), nullable=False)
