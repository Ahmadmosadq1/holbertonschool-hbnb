# part3/app/persistence/user_repository.py

from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def get(self, user_id: str) -> User:
        return self.session.query(User).get(user_id)

    def get_by_email(self, email: str) -> User:
        return self.session.query(User).filter_by(email=email).first()

    def all(self) -> list[User]:
        return self.session.query(User).all()

    def update(self, user_id: str, data: dict) -> User:
        user = self.get(user_id)
        if not user:
            return None
        for key, value in data.items():
            if key == 'password':
                user.password = value
            elif hasattr(user, key):
                setattr(user, key, value)
        self.session.commit()
        return user

    def delete(self, user_id: str) -> bool:
        user = self.get(user_id)
        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        return True
