from flask import request
from flask_restx import Namespace, Resource, fields
from app import db
from app.models.user import User

api = Namespace('users', description='User operations')

#─── Input model for creating a user ───────────────────────────────────────────
user_create_model = api.model('UserCreate', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name' : fields.String(required=True, description='Last name'),
    'email'     : fields.String(required=True, description='Email address'),
    'password'  : fields.String(required=True, description='Plain-text password'),
})

#─── POST /api/v1/users/ ────────────────────────────────────────────────────────
@api.route('/')
class UserList(Resource):
    @api.expect(user_create_model, validate=True)
    def post(self):
        data = request.get_json()

        # 1) Create & hash password in one go
        user = User(
            first_name=data['first_name'],
            last_name =data['last_name'],
            email     =data['email'],
            password  =data['password']
        )

        # 2) Persist
        db.session.add(user)
        db.session.commit()

        # 3) Return only id and message—no password!
        return {
            'id'     : user.id,
            'message': 'User successfully created'
        }, 201

#─── GET /api/v1/users/<user_id> ────────────────────────────────────────────────
@api.route('/<int:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)

        # Only expose non-sensitive fields
        return {
            'id'        : user.id,
            'first_name': user.first_name,
            'last_name' : user.last_name,
            'email'     : user.email
        }
