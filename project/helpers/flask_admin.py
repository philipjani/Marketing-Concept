from flask_admin.contrib.sqla import ModelView
from sqlalchemy import inspect


class ChronView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False

def init_admin(admin, db):
    from project import models

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


    admin.add_view(UsersView(models.Users, db.session, category="Main"))
    admin.add_view(ImagesView(models.Lead, db.session, category="Main"))
    admin.add_view(PlacesView(models.Template, db.session, category="Main"))
    admin.add_view(CharactersView(models.TextReply, db.session, endpoint="_textreply", category="Replies"))
    admin.add_view(NotesView(models.EmailReply, db.session, category="Replies"))
    admin.add_view(GamesView(models.Phone_Number, db.session, category="Assets"))
    admin.add_view(SessionsView(models.Email, db.session, category="Assets"))




