import csv


def dump_to_csv(table, db):
    with open("MC_dump", "wb") as file:
        outcsv = csv.writer(file)
        records = db.session.query(table).all()
        for curr in records:
            for column in table.__mapper__.columns:
                outcsv.writerow(getattr(curr, column.name))
                # print(getattr(curr, column.name))