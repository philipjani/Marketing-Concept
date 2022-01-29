
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required

from project.models import TextReply

replies = Blueprint("replies", __name__)

@replies.route('/replies', methods=["GET", 'POST'])
@login_required
def main():
    replies = TextReply.query.all()
    return render_template("replies.html", replies=replies)
