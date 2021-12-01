from .model_base import Base, db
import enum
from sqlalchemy import Enum


class RoleEnum(enum.Enum):
    user = 0
    admin = 1


class User(Base):
    __tablename__ = 'users'

    email = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    role = db.Column(Enum(RoleEnum), default=RoleEnum.user)
    active = db.Column(db.Boolean, default=True)
    team = db.relationship('Team', backref='users',
                           lazy=True, uselist=False)
