from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")  


class BaseRepository(Generic[T]):

    def __init__(self, model: type[T], db: Session, tenant_id: int | None = None):
        self.model = model
        self.db = db
        self.tenant_id = tenant_id

    def _query(self):
        query = self.db.query(self.model)
        if (
            self.tenant_id is not None
            and hasattr(self.model, "tenant_id")
        ):
            query = query.filter(self.model.tenant_id == self.tenant_id)
        if hasattr(self.model, "deleted"):
            query = query.filter(self.model.deleted.is_(False))
        return query

    def get(self, id: int) -> T | None:
        return self._query().filter(self.model.id == id).first()

    def list(self) -> list[T]:
        return self._query().all()

    def create(self, obj_data: dict) -> T:
        obj = self.model(**obj_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, obj_data: dict) -> T | None:
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

        if hasattr(obj, "deleted"):
            setattr(obj, "deleted", True)
            self.db.commit()
            return True

        self.db.delete(obj)
        self.db.commit()
        return True
