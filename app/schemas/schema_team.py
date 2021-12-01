from .schema_base import BaseSchema, ma
from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import validate


class TeamGetSchema(BaseSchema):

    class Meta:
        ordered = True
        include_fk = True

    name = ma.Str(dump_only=True)
    country = ma.Str(dump_only=True)
    team_value = ma.Integer(dump_only=True)
    budget = ma.Integer(dump_only=True)
    links = Hyperlinks({
        'self':
            URLFor('Teams.TeamById', values=dict(team_id='<id>')),
        'owner':
            URLFor('Users.UserById', values=dict(user_id='<user_id>')),
        'players':
            URLFor('Players.Players', values=dict(team_id='<id>'))
    })


class TeamPatchSchema(BaseSchema):
    name = ma.String(required=False,
                     validate=validate.Length(min=3, max=255))
    country = ma.String(required=False,
                        validate=validate.Length(min=3, max=255))
    budget = ma.Integer(required=False,
                        validate=validate.Range(min=0, min_inclusive=True,
                                                max=9223372036854775807,
                                                max_inclusive=True))
