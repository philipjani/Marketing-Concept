from flask_sqlalchemy import BaseQuery
from sqlalchemy.orm.scoping import scoped_session
from flask import flash

def convert(session: scoped_session):
    from project.models import Addresses
    if Addresses.query.filter_by(address="STOP_FLAG").first():
        flash("skipping update")
        return
    addys = separate_addresses(session)
    dups = delete_dups(session)
    flash(f"{addys} addresses separated.\n{dups} duplicate addresses deleted.")

def separate_addresses(session: scoped_session) -> int:
    from project.models import Lead, Addresses
    lead_query: BaseQuery = Lead.query
    address_query: BaseQuery = Addresses.query


    address = Addresses(address="STOP_FLAG")
    session.add(address)
    count = 0
    leads: list[Lead] = lead_query.all()
    for lead in leads:
        address = address_query.filter_by(address=lead.address).first()
        if not address:
            address = Addresses(
                address=lead.address,
                city=lead.city,
                state=lead.state,
                zip=lead.zip,
                owner_occupied=lead.owner_occupied,
                property_type=lead.property_type,
            )
            session.add(address)
            count += 1
        if address not in lead.addresses:
            lead.addresses.append(address)
            session.add(lead)
    return count

def delete_dups(session: scoped_session) -> int:
    from project.models import Addresses
    count = 0
    for address in Addresses.query.all():
        checking = Addresses.query.filter_by(address=address.address, city=address.city, state=address.state).all()
        if len(checking) > 1:
            for d in checking[1:]:
                count += 1
                session.delete(d)
    return count




        

    # address = address_query.filter_by(address=leads[0].address).first()
    # if not address:
    #     address = Addresses(
    #         address=leads[0].address,
    #         city=leads[0].city,
    #         state=leads[0].state,
    #         zip=leads[0].zip,
    #         owner_occupied=leads[0].owner_occupied,
    #         property_type=leads[0].property_type,
    #     )
    # print("addresses" in inspect(leads[0]).mapper.relationships)
    # print(leads[0].addresses)
    # for k, v in leads[0].__dict__.items():
    #     print(f'k: {k} || v: {v}')
    # print(leads[0].__mapper__.relationships)
    # if leads[0].addresses == []:
    #     leads[0].addresses.append(address)
    #     print("appended")
    # else:
    #     print("not")
    #     print(address in leads[0].addresses)












