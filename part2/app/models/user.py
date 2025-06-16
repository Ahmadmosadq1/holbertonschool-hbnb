import datetime


class User:

    def __init__(self, id: str, first_name: str, last_name: str, email: str, created_at: datetime, updated_at: datetime, is_admin: bool = False):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_admin = is_admin
        