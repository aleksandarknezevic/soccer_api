from .model_base import db, Base


class Token(Base):
    __tablename__ = 'tokens'

    jti = db.Column(db.String(120))
