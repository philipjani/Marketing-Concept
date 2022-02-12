from flask_login import current_user
from flask import redirect, url_for
from flask_admin import AdminIndexView, expose

class AdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_anonymous:
            return redirect(url_for("index.page"))

        return self.render('admin/index.html')