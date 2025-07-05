from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User

api = Namespace('auth', description='Authentication operations')

_login_model = api.model('Login', {
    'email':    fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(_login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        data = request.get_json() or {}
        email    = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Email and password are required'}, 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return {'error': 'Invalid credentials'}, 401

        token = create_access_token(identity={'id': str(user.id), 'is_admin': user.is_admin})
        return {'access_token': token}, 200


@api.route('/protected')
class Protected(Resource):
    @jwt_required()
    def get(self):
        """A protected endpoint that requires a valid JWT token"""
        identity = get_jwt_identity()
        return {'message': f'Hello, user {identity["id"]}'}, 200
