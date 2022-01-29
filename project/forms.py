
from flask_wtf import FlaskForm

from wtforms import widgets
from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import BooleanField, StringField, SubmitField, TextAreaField, PasswordField
from wtforms.widgets.core import TextArea
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError
from werkzeug.security import check_password_hash
from project.models import Users


# validators should be added to this
class FilterForm(FlaskForm):
    comp_select = SelectField("Filter by")
    length = IntegerField("Number of rows to display")
    info = StringField("Enter Filter Query")
    filter_submit = SubmitField("Go")

# class MultiCheckboxField(SelectMultipleField):
#     widget = widgets.TableWidget()
#     option_widget = widgets.CheckboxInput()

class LeadForm(FlaskForm):
    select = BooleanField()
    lead_submit = SubmitField("Skiptrace Leads")

# class TestForm(FlaskForm):
#     select = MultiCheckboxField('select')
#     test_submit = SubmitField("Skiptrace Leads")

class TemplateForm(FlaskForm):
    name = StringField("Name of Template")
    message = TextAreaField("Template body")
    template_submit = SubmitField("Save")

class ApplyForm(FlaskForm):
    apply_submit = SubmitField("Apply SMS Template to leads")

class ConfirmForm(FlaskForm):
    confirm_submit = SubmitField("Confirm")

class Login(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def validate_password(form, field):
        # the email is checked here as well so that the error will only print under the password field regardless of which field threw the error
        name_exists(form, field)
        password_compare(form, field)

    remember = BooleanField("Remember Me")
    login_submit = SubmitField("Submit")

def name_exists(form, field):
    if not Users.query.filter_by(name=form.name.data).first():
        raise ValidationError("There was a issue with your login. Check your credentials")

def password_compare(form, field):
    user = Users.query.filter_by(name=form.name.data).first()
    if not check_password_hash(user.hashed_password, field.data):
        raise ValidationError("There was a issue with your login. Check your credentials")