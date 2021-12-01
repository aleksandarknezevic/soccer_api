from .schema_base import BaseSchema, ma
from app.models import PositionEnum
from marshmallow_enum import EnumField
from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import validate


class PlayerGetSchema(BaseSchema):

    class Meta:
        ordered = True
        include_fk = True

    first_name = ma.Str(dump_only=True)
    last_name = ma.Str(dump_only=True)
    country = ma.Str(dump_only=True)
    age = ma.Integer(dump_only=True)
    market_value = ma.Integer(dump_only=True)
    position = EnumField(PositionEnum)
    links = Hyperlinks({
        'self':
            URLFor('Players.PlayerById', values=dict(player_id='<id>')),
        'team':
            URLFor('Teams.TeamById', values=dict(team_id='<team_id>'))
    })


class PlayerWriteSchema(BaseSchema):
    first_name = ma.String(required=False,
                           validate=validate.Length(min=3, max=255))
    last_name = ma.String(required=False,
                          validate=validate.Length(min=3, max=255))
    country = ma.String(required=False,
                        validate=validate.Length(min=3, max=255))
    market_value = ma.Integer(required=False,
                              validate=validate.Range(min=1,
                                                      min_inclusive=True,
                                                      max=9223372036854775807,
                                                      max_inclusive=True))
    position = ma.String(required=False,
                         validate=validate.OneOf([name for name in
                                                  dir(PositionEnum) if not
                                                  name.startswith('_')]))
    team_id = ma.Integer(required=False,
                         validate=validate.Range(min=0, min_inclusive=False,
                                                 max=9223372036854775807,
                                                 max_inclusive=True))
    age = ma.Integer(required=False,
                     validate=validate.Range(min=18, min_inclusive=True,
                                             max=40,
                                             max_inclusive=True))


class PlayerFiltersSchema(BaseSchema):
    team_id = ma.Integer(required=False,
                         validate=validate.Range(min=1, min_inclusive=True,
                                                 max=9223372036854775807,
                                                 max_inclusive=True))
