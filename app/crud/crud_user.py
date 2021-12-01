from typing import Any, Dict, Optional
from .crud_base import CRUDBase
from .crud_team import crud_team
from app.models import db, User, RoleEnum
from app.main.security import get_password_hash, check_password
from app.main.utils import get_random_country


class CRUDUser(CRUDBase[User]):
    def create(self, obj_in: Dict[str, Any]) -> User:
        new_user = User(
            email=obj_in['email'],
            password=get_password_hash(obj_in['password']),
            name=obj_in['name'],
        )
        if 'role' in obj_in:
            new_user.role = obj_in['role']
        team_data = {
            'name': obj_in['name'] + '\'s falcons',
            'country': get_random_country()
        }
        new_user.team = crud_team.generate_team(team_data)
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)
        return new_user

    def delete(self, user_id: int) -> User:
        user = self.get(user_id)

        user.active = False
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not check_password(password, user.password):
            return None
        if not self.is_active(user):
            return None
        return user

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        return User.query.filter(User.email == email).first()

    @staticmethod
    def is_admin(user: User) -> bool:
        if not user:
            return False
        return user.role == RoleEnum.admin

    @staticmethod
    def is_active(user: User) -> bool:
        return user.active


crud_user = CRUDUser(User)
