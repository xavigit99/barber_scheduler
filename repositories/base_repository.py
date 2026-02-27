from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session

T = TypeVar("T")  # Model type


class BaseRepository(Generic[T]):

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def list(self) -> List[T]:
        return self.db.query(self.model).all()

    def create(self, obj_data: dict) -> T:
        obj = self.model(**obj_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, obj_data: dict) -> Optional[T]:
        obj = self.get(id)
        if not obj:
            return None

        for key, value in obj_data.items():
            setattr(obj, key, value)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True