import os

def check_and_populate(app):

    with app.app_context():
        from project.models import Users, Phone_Number
        pw = os.environ.get("USER_PASS")
        if not Users.query.filter_by(name="Zack").first():
            Users.create(name="Zack", password=pw)
            print(f'User: "Zack" created..')
        if not Users.query.filter_by(name="Philip").first():
            Users.create(name="Philip", password=pw)
            print(f'User: "Philip" created..')
        if not Phone_Number.query.filter_by(mobile_phone="2062933922").first():
            Phone_Number.create(mobile_phone="2062933922")
            print("Zack's phone added")

