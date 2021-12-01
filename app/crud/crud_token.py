from .crud_base import CRUDBase
from app.models import db, Token


class CRUDToken(CRUDBase[Token]):
    @staticmethod
    def revoke(jti: str) -> None:
        token = Token()
        token.jti = jti
        db.session.add(token)
        db.session.commit()

    @staticmethod
    def is_revoked(jti: str) -> bool:
        query = Token.query.filter_by(jti=jti).first()
        return bool(query)


crud_token = CRUDToken(Token)
