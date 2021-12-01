from .schema_base import BaseSchema, ma
from app.models import RoleEnum
from marshmallow_enum import EnumField
from marshmallow import validate, EXCLUDE
from flask_marshmallow.fields import Hyperlinks, URLFor


class UserGetSchema(BaseSchema):
    class Meta:
        ordered = True
        include_fk = True
    name = ma.Str(dump_only=True)
    email = ma.Str(dump_only=True)
    role = EnumField(RoleEnum)
    active = ma.Boolean(dump_only=True)
    links = Hyperlinks({
        'self':
            URLFor('Users.UserById', values=dict(user_id='<id>')),
        'team':
            URLFor('Teams.TeamById', values=dict(team_id='<team.id>'))
    })


class UserRegisterSchema(BaseSchema):
    email = ma.String(required=True,
                      validate=[validate.Email(), validate.Length(max=255)])
    password = ma.String(load_only=True, required=True,
                         validate=validate.Length(min=4, max=50))
    name = ma.String(required=True,
                     validate=validate.Length(min=3, max=255))
    role = ma.String(validate=validate.OneOf([name for name in dir(RoleEnum)
                                              if not name.startswith('_')]))


class UserPatchSchema(BaseSchema):
    email = ma.String(required=False,
                      validate=[validate.Email(), validate.Length(max=255)])
    name = ma.String(required=False,
                     validate=validate.Length(min=3, max=255))
    password = ma.String(required=False,
                         validate=validate.Length(min=4, max=50))
    role = ma.String(validate=validate.OneOf([name for name in dir(RoleEnum)
                                              if not name.startswith('_')]))
    active = ma.Boolean(required=False)


class UserLoginSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    email = ma.String(required=True,
                      validate=[validate.Email(), validate.Length(max=255)])
    password = ma.String(required=True,
                         validate=validate.Length(min=4))
