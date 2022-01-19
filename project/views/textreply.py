from datetime import datetime
import pandas as pd
from flask import Blueprint, request, redirect, url_for, render_template, flash
import json
import os
import requests
from project.__init__ import db
from project.forms import ApplyForm, FilterForm, LeadForm
from project.models import db
from project import skiptracing as st
from project.models import TextReply, Phone_Number

textreply = Blueprint("textreply", __name__)

@textreply.route('/textreply', methods=['POST'])
def webhook():
    if request.method == 'POST':
        if type(request.json) is str:
            reply = json.loads(request.json)
        elif type(request.json) is dict:
            reply = request.json
        else:
            return


        
        print(f'dir(request): {dir(request)}')
        print(f'request: {request}')
        # reply = request.get_json()
        print(f'reply: {reply}')
        print(f'type(reply): {type(reply)}')
        # try:
        #     print(f'request.get_json(): {request.get_json()}')
        # except Exception as e:
        #     print(f'e: {e}')
        message = reply['text']
        number = reply['fromNumber']
        # try:
        #     contact_time = reply['contactTime']
        # except BaseException:
        #     contact_time = datetime.utcnow()
        phone_id = Phone_Number.query.filter_by(mobile_phone=number).first()
        if not phone_id:
            pass #make new contact. or log in someway
        else:
            TextReply.create(message=message, phone_id=phone_id, contact_time=datetime.utcnow())
            return f'{request.json}', 200
