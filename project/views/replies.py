
from flask import Blueprint, request, redirect, url_for, render_template, flash

from project.models import TextReply

replies = Blueprint("replies", __name__)

@replies.route('/replies', methods=["GET", 'POST'])
def main():
    replies = TextReply.query.all()
    return render_template("replies.html", replies=replies)
