from .model_base import db, Base


class Team(Base):
    __tablename__ = 'teams'

    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    team_value = db.Column(db.Integer, nullable=False, default=20000000)
    budget = db.Column(db.Integer, nullable=False, default=5000000)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'), unique=True, nullable=False)
    players = db.relationship('Player', backref='teams',
                              lazy='dynamic')
