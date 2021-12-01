from marshmallow import EXCLUDE

from .schema_base import ma


class TokenSchema(ma.Schema):
    class Meta:
        ordered = True
        unknown = EXCLUDE

    access_token = ma.String(required=False)
    refresh_token = ma.String(required=True)
    token_type = ma.String(required=True)
