
from flask_wtf import FlaskForm

from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField, TextAreaField
from wtforms.widgets.core import TextArea

# validators should be added to this
class FilterForm(FlaskForm):
    comp_select = SelectField("Filter by")
    length = IntegerField("Number of rows to display")
    info = StringField("Enter Filter Query")
    filter_submit = SubmitField("Go")

class TemplateForm(FlaskForm):
    name = StringField("Name of Template")
    message = TextAreaField("Template body")
    template_submit = SubmitField("Save")
    