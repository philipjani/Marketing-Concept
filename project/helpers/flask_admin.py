from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.orm.scoping import scoped_session


class ChronView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False

def init_admin(admin: Admin, db: SQLAlchemy):
    from project import models
    ss: scoped_session = db.session

    class UsersView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.Users).mapper.column_attrs]
    class ImagesView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.Lead).mapper.column_attrs]
    class GamesView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.Phone_Number).mapper.column_attrs]
    class CharactersView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.TextReply).mapper.column_attrs]
    class SessionsView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.Email).mapper.column_attrs]
    class NotesView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.EmailReply).mapper.column_attrs]
    class PlacesView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.Template).mapper.column_attrs]
    class AddressesView(ChronView):
        column_list = [c_attr.key for c_attr in inspect(models.Addresses).mapper.column_attrs]


    admin.add_view(UsersView(models.Users, ss, category="Main"))
    admin.add_view(ImagesView(models.Lead, ss, category="Main"))
    admin.add_view(PlacesView(models.Template, ss, category="Main"))
    admin.add_view(CharactersView(models.TextReply, ss, endpoint="_textreply", category="Replies"))
    admin.add_view(NotesView(models.EmailReply, ss, category="Replies"))
    admin.add_view(GamesView(models.Phone_Number, ss, category="Assets"))
    admin.add_view(SessionsView(models.Email, ss, category="Assets"))
    admin.add_view(AddressesView(models.Addresses, ss, category="Assets"))





