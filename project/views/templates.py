from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from project.forms import TemplateForm
from project.helpers.db_session import db_session

from project.models import db
from project.models import Template

templates = Blueprint("templates", __name__)

@templates.route('/templates', methods = ["POST", "GET"])
@login_required
def main():
    with db_session() as sess:
        form = TemplateForm()
        if request.method == 'POST':
            temp_name = form.name.data
            temp_message = form.message.data
            try:
                new_template = Template(name=temp_name, message=temp_message)
                sess.add(new_template)
                return redirect(url_for("templates.main"))
            except:
                return 'There was an issue adding your template.'
        else:
            sms_templates = Template.query.all()
        return render_template('templates.html', form=form, sms_templates=sms_templates)

@templates.route('/delete/<int:id>')
@login_required
def delete(id):
    sms_to_delete = Template.query.get_or_404(id)

    try:
        db.session.delete(sms_to_delete)
        db.session.commit()
        return redirect(url_for("templates.main"))
    except:
        return 'There was an error in deleting the template.'

@templates.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
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