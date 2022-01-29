from datetime import datetime
from flask import Blueprint, request
from flask_login import login_required
import json
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
        message = reply['text']
        number = reply['fromNumber']
        phone_id = Phone_Number.query.filter_by(mobile_phone=number).first()
        if not phone_id:
            pass #make new contact. or log in someway
        else:
            TextReply.create(message=message, phone_id=phone_id, contact_time=datetime.utcnow())
            return f'{request.json}', 200
