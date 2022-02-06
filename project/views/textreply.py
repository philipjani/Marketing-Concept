from datetime import datetime
from flask import Blueprint, request
import json
from project.models import TextReply, Phone_Number

textreply = Blueprint("textreply", __name__)


@textreply.route("/textreply", methods=["POST"])
def webhook():
    if request.method == "POST":
        if type(request.json) is str:
            reply = json.loads(request.json)
        elif type(request.json) is dict:
            reply = request.json
        else:
            return
        message = reply["text"]
        number = clean_number(reply["fromNumber"])
        phone = Phone_Number.query.filter_by(mobile_phone=number).first()
        if not phone:
            return f"{request.json}", 200
        else:
            TextReply.create(
                message=message, phone_id=phone.id, contact_time=datetime.utcnow()
            )
            return f"{request.json}", 200

def clean_number(num: str) -> str:
    if not num:
        return
    if num[0] == "+" and len(num) > 1:
        num = num[1:]
    if num[0] == "1" and len(num) > 1:
        num = num[1:]
    return num