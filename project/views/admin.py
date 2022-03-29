
from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_admin import AdminIndexView, expose
class AdminIndex(AdminIndexView):
    @expose('/', methods=["GET", "POST"])
    def index(self):

        from project.forms import ProperyType
        if current_user.is_anonymous:
            return redirect(url_for("index.page"))
        form = ProperyType()
        if request.method == "POST":
            remove_matches(form.types.data)
        form.types.choices = get_choices()
        return self.render('admin/index.html', form=form)

def get_choices():
    from project.models import Lead
    types = set()
    all = Lead.query.all()
    for L in all:
        types.add(L.property_type)
    return list(types)

def remove_matches(to_remove:list):
    from project.models import Lead
    from project.helpers.db_session import db_session
    with db_session() as sess:
        count = 0
        for rem in to_remove:
            removing = Lead.query.filter_by(property_type=rem).all()
            count += len(removing)
            for r in removing:
                sess.delete(r)
        flash(f"deleted {count} Leads")
