# part3/app/__init__.py

import os
from flask import Flask, jsonify
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or os.getenv('FLASK_CONFIG') or 'config.DevelopmentConfig')

    # init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # custom JWT error handlers
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify(error="Unauthorized action"), 403

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(error="Unauthorized action"), 403

    # register namespaces
    api = Api(app)
    from app.api.v1.users   import api as users_ns
    from app.api.v1.auth    import api as auth_ns
    from app.api.v1.places  import api as places_ns
    from app.api.v1.reviews import api as reviews_ns

    api.add_namespace(users_ns,  path='/api/v1/users')
    api.add_namespace(auth_ns,   path='/api/v1/auth')
    api.add_namespace(places_ns,  path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
