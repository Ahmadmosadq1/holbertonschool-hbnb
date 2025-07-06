# part3/app/models/user.py

from flask_bcrypt import generate_password_hash, check_password_hash
from app import db
from app.models.base_model import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    first_name   = db.Column(db.String(128), nullable=False)
    last_name    = db.Column(db.String(128), nullable=False)
    email        = db.Column(db.String(128), nullable=False, unique=True)
    password_hash= db.Column(db.String(128), nullable=False)
    is_admin     = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, plaintext):
        self.password_hash = generate_password_hash(plaintext).decode('utf-8')

    def verify_password(self, plaintext):
        return check_password_hash(self.password_hash, plaintext)
