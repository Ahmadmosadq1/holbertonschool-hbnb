# app/models/user.py

from app import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    is_admin   = db.Column(db.Boolean, default=False)
    password   = db.Column(db.String(128), nullable=False)

    def __init__(self, first_name: str, last_name: str, email: str,
                 password: str, is_admin: bool = False):
        # validate inputs
        if not first_name or len(first_name) > 50:
            raise ValueError("First name is required and must be <= 50 characters.")
        if not last_name or len(last_name) > 50:
            raise ValueError("Last name is required and must be <= 50 characters.")
        if not email or "@" not in email:
            raise ValueError("A valid email is required.")

        self.first_name = first_name
        self.last_name  = last_name
        self.email      = email
        self.is_admin   = is_admin

        # hash and store the password
        self.hash_password(password)

    def hash_password(self, password: str) -> None:
        """Hash plaintext password and store in field."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Verify plaintext password against stored hash."""
        return bcrypt.check_password_hash(self.password, password)
