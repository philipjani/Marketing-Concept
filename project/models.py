from project.__init__ import db

class BaseMixin():
    @classmethod
    def create(cls, **kw):
        """adds new item to database

        this is inherited by all SQLAlchemy classes
        """
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj

class Lead(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer) #just added
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


class Phone_Number(BaseMixin, db.Model):
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


class TextReply(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(2000), nullable=False)
    contact_time = db.Column(db.DateTime)
    phone_id = db.Column(db.Integer, db.ForeignKey('phone_number.id'))

    def __repr__(self):
        return f'<TextReply: {self.id}>'


class Email(BaseMixin, db.Model):
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


class EmailReply(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    contact_time = db.Column(db.DateTime)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'))

    def __repr__(self):
        return f'<EmailReply: {self.id}>'


class Template(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Template: {self.id}>'