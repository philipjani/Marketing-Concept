from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_admin import AdminIndexView, expose
from sqlalchemy.orm.scoping import scoped_session
from project.helpers.address_convert import convert

class AdminIndex(AdminIndexView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        from project.models import Lead
        from project.forms import RemoveProperyType, RemoveMLSPending, RemoveLLC
        from project.helpers.db_session import db_session

        sess: scoped_session

        with db_session() as sess:
            if current_user.is_anonymous:
                return redirect(url_for("index.page"))

            # forms
            form_rm_by_property_type = RemoveProperyType(prefix="removepropertytype")
            form_rm_mls_pendings = RemoveMLSPending(prefix="removemlspending")
            form_rm_llcs = RemoveLLC(prefix="removellc")

            llcs = Lead.get_llcs()
            mls_pendings = Lead.query.filter_by(mls_status="PENDING").all()

            convert(sess)
            if request.method == "POST":
                if form_rm_by_property_type.submit.data:
                    property_types = Lead.get_property_types()
                    count = 0
                    for property_type in property_types:
                        rows_with_type = Lead.query.filter_by(
                            property_type=property_type
                        ).all()
                        count += len(rows_with_type)
                        Lead.delete_rows(rows_with_type, sess)
                elif form_rm_mls_pendings.submit.data:
                    count = len(mls_pendings)
                    Lead.delete_rows(mls_pendings, sess)
                elif form_rm_llcs.submit.data:
                    count = len(llcs)
                    Lead.delete_rows(llcs, sess)
                    llcs = Lead.get_llcs()
                flash(f"deleted {count} rows") if count > 0 else flash(
                    "nothing to delete"
                )
            form_rm_by_property_type.types.choices = Lead.get_property_types()

            return self.render(
                "admin/index.html",
                property_type=form_rm_by_property_type,
                mls=form_rm_mls_pendings,
                llc=form_rm_llcs,
                mls_amount=len(mls_pendings),
                llcs_amount=len(llcs),
            )
