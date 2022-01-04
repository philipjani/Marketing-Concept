import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash
from project.forms import TemplateForm

from project.models import db
from project.models import Lead, Template, TextReply

templates = Blueprint("templates", __name__)

@templates.route('/templates', methods = ["POST", "GET"])
def main():
    form = TemplateForm()
    if request.method == 'POST':
        temp_name = form.name.data
        temp_message = form.message.data
        try:
            Template.create(name=temp_name, message=temp_message)
            return redirect(url_for("templates.main"))
        except:
            return 'There was an issue adding your template.'
    else:
        #https://stackoverflow.com/questions/2633218/how-can-i-select-all-rows-with-sqlalchemy/26217436
        sms_templates = Template.query.all()
    return render_template('templates.html', form=form, sms_templates=sms_templates)

@templates.route('/delete/<int:id>')
def delete(id):
    sms_to_delete = Template.query.get_or_404(id)

    try:
        #https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
        db.session.delete(sms_to_delete)
        db.session.commit()
        return redirect(url_for("templates.main"))
    except:
        return 'There was an error in deleting the template.'

@templates.route('/update/<int:id>', methods=['GET', 'POST'])
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