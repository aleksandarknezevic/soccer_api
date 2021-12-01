from .model_base import Base, db
import enum
from sqlalchemy import Enum


class PositionEnum(enum.Enum):
    goalkeeper = ['GK', 3]
    defender = ['DF', 6]
    midfielder = ['MF', 6]
    attacker = ['FW', 5]


class Player(Base):
    __tablename__ = 'players'

    first_name = db.Column(db.String(255), nullable=False, default='John')
    last_name = db.Column(db.String(255), nullable=False, default='Wick')
    age = db.Column(db.Integer, nullable=False, default=28)
    country = db.Column(db.String(255), nullable=False, default='Serbia')
    market_value = db.Column(db.Integer, nullable=False, default=1000000)
    position = db.Column(Enum(PositionEnum), default=PositionEnum.attacker)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    transfer = db.relationship('Transfer',
                               cascade='all, delete-orphan', uselist=False)
