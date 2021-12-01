from typing import Any, Generic, Dict, List, Optional, Type, TypeVar
from app.models import db, Base
from sqlalchemy.exc import IntegrityError
from app.main.security import get_password_hash

ModelType = TypeVar('ModelType', bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, id: Any) -> Optional[ModelType]:
        return self.model.query.filter(self.model.id == id).first()

    def get_all(self) -> List[ModelType]:
        return self.model.query.all()

    def create(self, obj_in: Dict[str, Any]) -> Dict[str, Any]:
        obj: ModelType = self.model()
        for field in obj_in:
            setattr(obj, field, obj_in[field])
        try:
            db.session.add(obj)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'added': False}
        db.session.refresh(obj)
        return obj

    @staticmethod
    def update(
        db_obj: ModelType,
        obj_in: Dict[str, Any],
    ) -> Dict[str, Any]:
        for field in obj_in:
            if field in obj_in:
                if field == 'password':
                    setattr(db_obj, field, get_password_hash(obj_in[field]))
                else:
                    setattr(db_obj, field, obj_in[field])
        db.session.add(db_obj)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'added': False}
        db.session.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> ModelType:
        obj = db.session.query(self.model).get(id)
        db.session.delete(obj)
        db.session.commit()
        return obj
