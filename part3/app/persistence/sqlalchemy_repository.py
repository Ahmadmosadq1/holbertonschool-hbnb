# part3/app/persistence/sqlalchemy_repository.py

from abc import ABC, abstractmethod
from typing import Type, List, Any
from sqlalchemy.orm import Session

class SQLAlchemyRepository(ABC):
    def __init__(self, model: Type, session: Session):
        self.model = model
        self.session = session

    def add(self, obj: Any) -> Any:
        self.session.add(obj)
        self.session.commit()
        return obj

    def get(self, obj_id: str) -> Any:
        return self.session.query(self.model).get(obj_id)

    def all(self) -> List[Any]:
        return self.session.query(self.model).all()

    def get_by_attribute(self, attr: str, value: Any) -> Any:
        return self.session.query(self.model).filter(getattr(self.model, attr)==value).first()

    def update(self, obj_id: str, data: dict) -> Any:
        obj = self.get(obj_id)
        if not obj:
            return None
        for key, val in data.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        self.session.commit()
        return obj

    def delete(self, obj_id: str) -> bool:
        obj = self.get(obj_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True
