import uuid

from flask import request, abort
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User

api = Namespace('users', description='User operations')

# Model for input validation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description="User's first name"),
    'last_name': fields.String(required=True, description="User's last name"),
    'email': fields.String(required=True, description="User's email"),
    'password': fields.String(required=True, description="User's password")
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model)
    def post(self):
        """Create a new user"""
        data = request.get_json() or {}
        # Input fields will be validated by User constructor
        try:
            user = User(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email'),
                password=data.get('password')
            )
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Email already exists'}, 400
        except ValueError as ve:
            return {'error': str(ve)}, 400

        return {'id': user.id, 'message': 'User successfully created'}, 201

@api.route('/<int:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        """Retrieve user details (excluding password)"""
        user = User.query.get_or_404(user_id)
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_admin': user.is_admin
        }

    def delete(self, user_id):
        """Delete a user"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted'}, 200
