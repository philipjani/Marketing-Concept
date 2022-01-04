
def init_blueprints(app):

    from project.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from project.views.index import index as index_blueprint
    app.register_blueprint(index_blueprint)

    from project.views.leads import leads as leads_blueprint
    app.register_blueprint(leads_blueprint)

    from project.views.templates import templates as templates_blueprint
    app.register_blueprint(templates_blueprint)

    return
    
