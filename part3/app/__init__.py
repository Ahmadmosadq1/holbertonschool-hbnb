import os
from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# extensions
db    = SQLAlchemy()
bcrypt = Bcrypt()
jwt    = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    # load your config (must set SECRET_KEY)
    app.config.from_object(config_class or os.getenv('FLASK_CONFIG') or 'config.DevelopmentConfig')

    # ensure JWTs are signed with our SECRET_KEY
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']

    # init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # register namespaces
    api = Api(app)
    from app.api.v1.users import api as users_ns
    from app.api.v1.auth import api  as auth_ns

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(auth_ns,  path='/api/v1/auth')

    return app
