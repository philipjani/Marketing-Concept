
def init_blueprints(app):

    from project.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from project.views.index import index as index_blueprint
    app.register_blueprint(index_blueprint)

    return
