import os

import sqlite3
import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, abort

from project.models import db
from project import skiptracing as st
from project.models import Lead, Template, TextReply

main = Blueprint("main", __name__)

# @main.route('/templates', methods = ["POST", "GET"])
# def templates():
#     if request.method == 'POST':
#         temp_name = request.form['name']
#         temp_message = request.form['message']
#         sms = Template(name=temp_name, message=temp_message)
#         try:
#             db.session.add(sms)
#             db.session.commit()
#             return redirect('/templates')
#         except:
#             return 'There was an issue adding your template.'
#     else:
#         #https://stackoverflow.com/questions/2633218/how-can-i-select-all-rows-with-sqlalchemy/26217436
#         sms_templates = Template.query.all()
#         return render_template('templates.html', sms_templates=sms_templates)

# @main.route('/delete/<int:id>')
# def delete(id):
#     sms_to_delete = Template.query.get_or_404(id)

#     try:
#         #https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
#         db.session.delete(sms_to_delete)
#         db.session.commit()
#         return redirect('/templates')
#     except:
#         return 'There was an error in deleting the template.'

# @main.route('/update/<int:id>', methods=['GET', 'POST'])
# def update(id):
#     template_update = Template.query.get_or_404(id)
    
#     if request.method == 'POST':
#         template_update.name = request.form['name']
#         template_update.message = request.form['message']

#         try:
#             db.session.commit()
#             return redirect('/templates')
#         except:
#             return 'There was an error editing the template.'
#     else:
#         return render_template('update.html', template_update=template_update)

@main.route('/admin', methods=['GET'])
def admin():
    replies = TextReply.query.all()
    return render_template('admin.html', replies=replies)


@main.route('/textreply', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        reply = request.json
        print(f'dir(reply): {dir(reply)}')
        message = reply['text']
        number = reply['fromNumber']
        # try:
        #     contact_time = reply['contactTime']
        # except BaseException:
        #     contact_time = datetime.utcnow()
        TextReply.create(message=message, phone_id=number)
        return f'{request.json}', 200
    else:
        abort(400)

@main.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

@main.errorhandler(500)
def page_not_found(error):
   return render_template('500.html', title = '500'), 500