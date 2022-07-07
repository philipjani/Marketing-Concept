import os

import flask_migrate

from sqlalchemy_utils.functions import database_exists
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_admin import Admin

from project.views.admin import AdminIndex

from project.helpers.flask_login import config as config_fl
from project.blueprints import init_blueprints
from project.helpers.populate_users import check_and_populate
from project.helpers.flask_admin import init_admin

db = SQLAlchemy()
admin = Admin(name="marketing_concept", template_mode="bootstrap3")
migrate_ = Migrate()
socketio = SocketIO(cors_allowed_origins="*")
login_manager = config_fl()


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    try:
        app = Flask(__name__)
        config(app)
        db.init_app(app)
        with app.app_context():
            from project import models
        migrate_.init_app(app, db, compare_type=True)
        ready_db(app, test_config)
        check_and_populate(app)
        init_blueprints(app)
        login_manager.init_app(app)
        socketio.init_app(app)
        init_admin(admin, db)
        admin.init_app(app, AdminIndex())
        # separate_addresses(app)
        return app
    except Exception as e:
        print(f"e: {e}")


# def separate_addresses(app):
#     from project.helpers.db_session import db_session
#     from project.models import Lead, Addresses
#     import random

    # with app.app_context():
    #     with db_session(autocommit=False) as sess:
    #         if not Lead.query.filter_by(first_name="zack_test3").first():
    #             leads = Lead.query.all()
    #             test = Lead(first_name="zack_test3")
    #             sess.add(test)
    #             sess.commit()
    #             for i in range(10):
    #                 for j in range(random.randint(1, 5)):
    #                     k = i + 10 + j
    #                     new = Lead(
    #                         first_name=leads[i].first_name,
    #                         last_name=leads[i].last_name,
    #                         age=leads[i].age,
    #                         address=leads[k].address,
    #                         city=leads[k].city,
    #                         state=leads[k].state,
    #                         zip=leads[k].zip,
    #                         owner_occupied=leads[k].owner_occupied,
    #                         property_type=leads[k].property_type,
    #                         mls_status=leads[i].mls_status,
    #                     )
    #                     sess.add(new)
    #             sess.commit()
    #         else:
    #             print(f"not")
    #         addresses = Addresses.query.all()
    #         for a in addresses:
    #             sess.delete(a)
    #         sess.commit()
    #         addresses = Addresses.query.all()
    #         if len(addresses) > 0:
    #             print(f"there are: {len(addresses)} addresses")
    #         else:
    #             leads = Lead.query.all()
    #             for lead in leads:
    #                 if lead.address:
    #                     new = Addresses(
    #                         address=lead.address,
    #                         city=lead.city,
    #                         state=lead.state,
    #                         zip=lead.zip,
    #                         owner_occupied=lead.owner_occupied,
    #                         lead_id=lead.id,
    #                     )
    #                     sess.add(new)
    #         to_combine = {}
    #         multis = {}
    #         addresses = Addresses.query.all()

    #         print(f"there are now: {len(addresses)} addresses")
    #         for address in addresses:
    #             dups = Addresses.query.filter_by(
    #                 address=address.address,
    #                 city=address.city,
    #                 state=address.state,
    #                 zip=address.zip,
    #             ).all()
    #             if len(dups) > 1:
    #                 to_combine[dups[0].address] = []
    #                 for dup in dups:
    #                     to_combine[dups[0].address].append(dup.lead_id)
    #             multi = Addresses.query.filter_by(lead_id=address.lead_id).all()
    #             if len(multi) > 1:
    #                 for m in multi:
    #                     multis[m.lead_id] = m
    #         print(f"m: {multis}")
    #         print(f"to_combine: {to_combine}")
    #         for address, lead in to_combine.items():
    #             for lead_id in address:
    #                 lead = Lead.query.get(lead_id)
    #                 # if lead.first_name == 
    #         sess.commit()


def config(app):
    db_password = os.environ.get("MC_PASS")
    config_db_uri(app)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SECRET_KEY"] = db_password
    app.config["POSTGRES_PASSWORD"] = db_password


def config_db_uri(app):
    db_password = os.environ.get("MC_PASS")
    # Heroku
    if os.environ.get("_HEROKU_HOSTING"):
        print("connecting to heroku...")
        uri = postfix(os.environ.get("DATABASE_URL"))
    # local
    elif os.environ.get("DOCKER_FLAG"):
        print("connecting to local through docker...")
        uri = f"postgresql://postgres:{db_password}@mc_database:5432/mc_db"
    else:
        print("connecting to local...")
        uri = "sqlite:///test.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    if not database_exists(uri):
        print("creating database..")
        create_db()
        config_db_uri(app)
    print(f"database found")
    return


def postfix(string):
    """replaces depreciated 'postgres:' with 'postgresql'"""
    if string is None:
        return None
    else:
        if string[0:9] == "postgres:":
            new = "postgresql" + string[8:]
            return new
        else:
            return string


def ready_db(app, test_config):
    """Sets up db with Flask Migrate"""
    if test_config is not None:
        app.config.update(test_config)
        return
    with app.app_context():
        try:
            flask_migrate.upgrade()
            print("database upgraded successfully")
        except Exception as e:
            print(e)
            raise RuntimeError(
                """Flask Migrations/versions directory either not found or empty.\n 
                check your Migrations directory errors"""
            )
    return


def create_db():
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    db_password = os.environ.get("MC_PASS")
    con = psycopg2.connect(
        f"host='mc_database' user='postgres' password='{db_password}'"
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = con.cursor()
    name_Database = "mc_db"
    cursor.execute(f"DROP DATABASE IF EXISTS {name_Database};")
    sqlCreateDatabase = "create database " + name_Database + ";"
    cursor.execute(sqlCreateDatabase)
    print(f"{name_Database} created")
    return
