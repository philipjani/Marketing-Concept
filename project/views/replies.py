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
from project.models import TextReply

replies = Blueprint("replies", __name__)

@replies.route('/replies', methods=["GET", 'POST'])
def main():
    replies = TextReply.query.all()
    return render_template("replies.html", replies=replies)
