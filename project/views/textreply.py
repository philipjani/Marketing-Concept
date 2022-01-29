from datetime import datetime
from flask import Blueprint, request
from flask_login import login_required
import json
from project.models import TextReply, Phone_Number

textreply = Blueprint("textreply", __name__)


@textreply.route("/textreply", methods=["POST"])
def webhook():
    if request.method == "POST":
        print(f"received")
        print(f"request: {request}")
        print(f"request.json: {request.json}")
        if type(request.json) is str:
            print(f"request.json str: {request.json}")
            reply = json.loads(request.json)
        elif type(request.json) is dict:
            print(f"request.json dict: {request.json}")
            reply = request.json
        else:
            return
        message = reply["text"]
        number = clean_number(reply["fromNumber"])
        print(number)
        for n in number:
            print(n, type(n))
        phone = Phone_Number.query.filter_by(mobile_phone=number).first()
        if not phone:
            print(f"not found")
            return f"{request.json}", 200
        else:
            print(f"found")
            TextReply.create(
                message=message, phone_id=phone.id, contact_time=datetime.utcnow()
            )
            return f"{request.json}", 200

def clean_number(num: str) -> str:
    if not num:
        return
    print(num)
    if num[0] == "+" and len(num) > 1:
        num = num[1:]
    print(num)
    if num[0] == "1" and len(num) > 1:
        num = num[1:]
    print(num)
    return num