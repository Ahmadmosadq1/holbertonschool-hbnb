# part3/app/api/v1/users.py

import uuid
from flask       import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User

api = Namespace('users', description='User operations')

# Model for user creation (now includes password)
user_model = api.model('User', {
    'first_name': fields.String(required=True, description="User's first name"),
    'last_name':  fields.String(required=True, description="User's last name"),
    'email':      fields.String(required=True, description="User's email"),
    'password':   fields.String(required=True, description="User's password")
})

# Model for user update (no email/password)
update_user_model = api.model('UserUpdate', {
    'first_name': fields.String(required=True, description="User's first name"),
    'last_name':  fields.String(required=True, description="User's last name"),
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(409, 'User already exists')
    def post(self):
        """Create a new user"""
        data = api.payload
        try:
            new_user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email']
            )
            new_user.password = data['password']
            db.session.add(new_user)
            db.session.commit()
            return {
                'id':         new_user.id,
                'first_name': new_user.first_name,
                'last_name':  new_user.last_name,
                'email':      new_user.email,
                'is_admin':   new_user.is_admin
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'User with this email already exists'}, 409
        except Exception as e:
            return {'error': str(e)}, 400

    # ... rest unchanged ...
