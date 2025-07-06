# part3/app/services/facade.py

from app.persistence.user_repository import UserRepository
from app.persistence.repository import InMemoryRepository
from app.models.user    import User
from app.models.amenity import Amenity
from app.models.place   import Place
from app.models.review  import Review
from app import db

class HBnBFacade:
    def __init__(self):
        # SQLAlchemy-backed user repo
        self.user_repo    = UserRepository(db.session)
        # in-memory for others
        self.amenity_repo = InMemoryRepository()
        self.place_repo   = InMemoryRepository()
        self.review_repo  = InMemoryRepository()

    # --- User methods ---
    def create_user(self, user_data):
        user = User(**user_data)
        return self.user_repo.add(user)

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_email(email)

    def get_users(self):
        return self.user_repo.all()

    def update_user(self, user_id, data):
        return self.user_repo.update(user_id, data)

    def delete_user(self, user_id):
        return self.user_repo.delete(user_id)

    # --- Amenity methods ---
    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    # ... rest unchanged ...
