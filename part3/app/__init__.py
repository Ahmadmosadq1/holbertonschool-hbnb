import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api

from config import config

# instantiate extensions
bcrypt = Bcrypt()
db     = SQLAlchemy()

def create_app(config_name=None):
    """Application factory: create & configure the Flask app."""
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # init extensions
    bcrypt.init_app(app)
    db.init_app(app)

    # ensure all model modules are imported so SQLAlchemy knows about tables
    from app.models.user      import User
    from app.models.amenity   import Amenity
    from app.models.place     import Place
    from app.models.review    import Review

    # auto-create tables in dev & test
    if config_name in ('development', 'testing', 'default'):
        with app.app_context():
            db.create_all()

    # build the REST API
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API'
    )

    # import and register namespaces
    from app.api.v1.users      import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places     import api as places_ns
    from app.api.v1.reviews    import api as reviews_ns

    api.add_namespace(users_ns,     path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns,    path='/api/v1/places')
    api.add_namespace(reviews_ns,   path='/api/v1/reviews')

    return app
