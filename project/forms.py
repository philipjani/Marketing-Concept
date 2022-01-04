
from flask_wtf import FlaskForm

from wtforms import widgets
from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.widgets.core import TextArea

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
