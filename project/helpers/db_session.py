from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from project.__init__ import db
from sqlalchemy.orm.scoping import scoped_session
@contextmanager
def db_session(autocommit=True) -> scoped_session:
    session: scoped_session = db.session
    try:
        yield session
        if autocommit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.remove()
