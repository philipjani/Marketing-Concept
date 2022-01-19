
def init_blueprints(app):


    from project.views.index import index as index_blueprint
    app.register_blueprint(index_blueprint)

    from project.views.leads import leads as leads_blueprint
    app.register_blueprint(leads_blueprint)

    from project.views.templates import templates as templates_blueprint
    app.register_blueprint(templates_blueprint)

    from project.views.apply_template import apply as apply_blueprint
    app.register_blueprint(apply_blueprint)

    from project.views.textreply import textreply as textreply_blueprint
    app.register_blueprint(textreply_blueprint)

    from project.views.replies import replies as replies_blueprint
    app.register_blueprint(replies_blueprint)
    return
    
