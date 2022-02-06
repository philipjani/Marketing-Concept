import os

import flask_migrate

from sqlalchemy_utils.functions import database_exists
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from project.helpers.flask_login import config as config_fl
from project.blueprints import init_blueprints
from project.helpers.populate_users import check_and_populate

db = SQLAlchemy()
migrate_ = Migrate()
socketio = SocketIO(cors_allowed_origins="*")
login_manager = config_fl()

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    try:
        app = Flask(__name__)
        config(app)
        db.init_app(app)
        migrate_.init_app(app, db, compare_type=True)
        ready_db(app, test_config)
        check_and_populate(app)
        init_blueprints(app)
        login_manager.init_app(app)
        socketio.init_app(app)

        return app
    except Exception as e:
        print(f'e: {e}')



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
    print(f'database found')
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
        except Exception:
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
