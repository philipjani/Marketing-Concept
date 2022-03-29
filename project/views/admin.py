
from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_admin import AdminIndexView, expose
class AdminIndex(AdminIndexView):
    @expose('/', methods=["GET", "POST"])
    def index(self):
        from project.models import Lead

        from project.forms import ProperyType, MLSStatus
        if current_user.is_anonymous:
            return redirect(url_for("index.page"))
        property_type = ProperyType(prefix="propertytype")
        mls = MLSStatus(prefix="mlsstatus")
        mls_amount = len(Lead.query.filter_by(mls_status="PENDING").all())
        if request.method == "POST":
            if property_type.submit.data:
                remove_property_type(property_type.types.data)
            elif mls.submit.data:
                remove_mls()
                mls_amount = len(Lead.query.filter_by(mls_status="PENDING").all())
        property_type.types.choices = get_choices()
        return self.render('admin/index.html', property_type=property_type, mls=mls, mls_amount=mls_amount)

def get_choices():
    from project.models import Lead
    types = set()
    all = Lead.query.all()
    for L in all:
        types.add(L.property_type)
    return list(types)

def remove_mls():
    from project.models import Lead
    from project.helpers.db_session import db_session

    with db_session() as sess:
        to_delete = Lead.query.filter_by(mls_status="PENDING").all()
        count = len(to_delete)
        for rem in to_delete:
            sess.delete(rem)
        flash(f"deleted {count} Leads") if count > 0 else flash("nothing to delete")


def remove_property_type(to_remove:list):
    from project.models import Lead
    from project.helpers.db_session import db_session
    with db_session() as sess:
        count = 0
        for rem in to_remove:
            removing = Lead.query.filter_by(property_type=rem).all()
            count += len(removing)
            for r in removing:
                sess.delete(r)
        flash(f"deleted {count} Leads") if count > 0 else flash("nothing to delete")
