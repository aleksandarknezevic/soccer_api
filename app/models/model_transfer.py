from .model_base import db, Base


class Transfer(Base):
    __tablename__ = 'transfers'

    price = db.Column(db.Integer, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'),
                          unique=True, nullable=False)
    player = db.relationship('Player',
                             uselist=False, back_populates='transfer')
