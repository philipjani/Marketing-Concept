from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_admin import AdminIndexView, expose


class AdminIndex(AdminIndexView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        from project.models import Lead
        from project.forms import RemoveProperyType, RemoveMLSPending, RemoveLLC
        if current_user.is_anonymous:
            return redirect(url_for("index.page"))
        property_type = RemoveProperyType(prefix="removepropertytype")
        mls = RemoveMLSPending(prefix="removemlspending")
        llc = RemoveLLC(prefix="removellc")
        if request.method == "POST":
            if property_type.submit.data:
                remove_property_type(property_type.types.data)
            elif mls.submit.data:
                remove_mls()
            elif llc.submit.data:
                llcs = get_llcs()
                remove_llc(llcs)
        property_type.types.choices = get_choices()
        return self.render(
            "admin/index.html",
            property_type=property_type,
            mls=mls,
            mls_amount=len(Lead.query.filter_by(mls_status="PENDING").all()),
            llc=llc,
            llcs_amount = get_llcs()["count"],
        )


def get_choices():
    from project.models import Lead

    types = set()
    all = Lead.query.all()
    for L in all:
        types.add(L.property_type)
    return list(types)


def get_llcs():
    from project.models import Lead

    count = 0
    all = Lead.query.all()
    llcs = []
    for rem in all:
        if rem.first_name and "llc" in rem.first_name.lower() or "llc" in rem.last_name.lower():
            print(rem.first_name, rem.last_name)
            llcs.append(rem)
            count += 1
    return {"count": count, "llcs": llcs}


def remove_llc(llcs):
    from project.helpers.db_session import db_session

    with db_session() as sess:
        for rem in llcs["llcs"]:
            sess.delete(rem)
        flash(f"deleted {llcs['count']} Leads") if llcs["count"] > 0 else flash(
            "nothing to delete"
        )


def remove_mls():
    from project.models import Lead
    from project.helpers.db_session import db_session

    with db_session() as sess:
        to_delete = Lead.query.filter_by(mls_status="PENDING").all()
        count = len(to_delete)
        for rem in to_delete:
            sess.delete(rem)
        flash(f"deleted {count} Leads") if count > 0 else flash("nothing to delete")


def remove_property_type(to_remove: list):
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
