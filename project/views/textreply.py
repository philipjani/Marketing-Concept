from __future__ import annotations

from datetime import datetime
from flask import Blueprint, request
import json
from project.helpers.db_session import db_session
from project.models import TextReply, Phone_Number, convert_phone
from sqlalchemy.orm.scoping import scoped_session
from project.models import Lead

textreply = Blueprint("textreply", __name__)


@textreply.route("/textreply", methods=["POST"])
def webhook():
    # TODO clean this up
    sess: scoped_session
    with db_session() as sess:
        if type(request.json) is str:
            reply = json.loads(request.json)
        elif type(request.json) is dict:
            reply = request.json
        else:
            return
        number = convert_phone(reply["fromNumber"])
        phone: Phone_Number = Phone_Number.query.filter_by(mobile_phone=number).first()
        message = reply["text"]
        if not phone:
            return f"{request.json}", 200
        new_text = TextReply(
            message=message, phone_id=phone.id, contact_time=datetime.utcnow()
        )
        sess.add(new_text)
        return f"{request.json}", 200

