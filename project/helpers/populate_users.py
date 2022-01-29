import os

def check_and_populate(app):

    with app.app_context():
        from project.models import Users
        pw = os.environ.get("USER_PASS")
        if not Users.query.filter_by(name="Zack").first():
            Users.create(name="Zack", password=pw)
            print(f'User: "Zack" created..')
        if not Users.query.filter_by(name="Philip").first():
            Users.create(name="Philip", password=pw)
            print(f'User: "Philip" created..')


