import datetime


class Amenity:
    def __init__(self, id: str, name: str, created_at: datetime.datetime, updated_at: datetime.datetime):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at
