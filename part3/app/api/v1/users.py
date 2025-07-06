# part3/app/api/v1/users.py

import uuid
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description="User's first name"),
    'last_name':  fields.String(required=True, description="User's last name"),
    'email':      fields.String(required=True, description="User's email"),
    'password':   fields.String(required=False, description="User's password (optional)")
})

update_user_model = api.model('UserUpdate', {
    'first_name': fields.String(description="User's first name"),
    'last_name':  fields.String(description="User's last name"),
    'email':      fields.String(description="User's email"),
    'password':   fields.String(description="User's password")
})


@api.route('/')
class UserList(Resource):
    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(403, 'Admin privileges required')
    @api.response(409, 'User already exists')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new user (admin only)"""
        current = get_jwt_identity()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        data = api.payload
        try:
            new_user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email']
            )
            # use provided password or generate a random one
            pw = data.get('password') or uuid.uuid4().hex
            new_user.password = pw
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

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve all users (public)"""
        users = User.query.all()
        return [{
            'id':         u.id,
            'first_name': u.first_name,
            'last_name':  u.last_name,
            'email':      u.email,
            'is_admin':   u.is_admin
        } for u in users], 200

# ... rest unchanged ...
