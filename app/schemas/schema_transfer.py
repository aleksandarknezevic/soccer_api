from .schema_base import BaseSchema, ma
from .schema_player import PlayerGetSchema
from marshmallow import validate, validates_schema, ValidationError
from flask_marshmallow.fields import Hyperlinks, URLFor


class TransferGetSchema(BaseSchema):

    class Meta:
        ordered = True
        include_fk = True

    price = ma.Integer(dump_only=True)
    player = ma.Nested(PlayerGetSchema, many=False)
    links = Hyperlinks({
        'self':
            URLFor('Transfers.TransferById', values=dict(transfer_id='<id>')),
    })


class TransferWriteSchema(BaseSchema):

    price = ma.Integer(required=True,
                       validate=validate.Range(min=0, min_inclusive=False,
                                               max=9223372036854775807,
                                               max_inclusive=True))
    player_id = ma.Integer(required=True,
                           validate=validate.Range(min=0, min_inclusive=False,
                                                   max=9223372036854775807,
                                                   max_inclusive=True))


class TransferPatchSchema(BaseSchema):
    price = ma.Integer(required=True,
                       validate=validate.Range(min=0, min_inclusive=False,
                                               max=9223372036854775807,
                                               max_inclusive=True))


class TransferFilterSchema(BaseSchema):
    @validates_schema
    def validate_price(self, data, **kwargs):
        if (
               ('price' in data and 'price_gt' in data)
           ):
            raise ValidationError('Only one of price and price_gt is allowed')
        if (
               ('price' in data and 'price_lt' in data)
           ):
            raise ValidationError('Only one of price and price_lt is allowed')
        if (
               ('price_lt' in data and 'price_gt' in data) and
               data['price_lt'] <= data['price_gt']
           ):
            raise ValidationError('price_lt must be greater than price_gt')

        if (
               ('value' in data and 'value_gt' in data)
           ):
            raise ValidationError('Only one of value and value_gt is allowed')
        if (
               ('value' in data and 'value_lt' in data)
           ):
            raise ValidationError('Only one of value and value_lt is allowed')
        if (
               ('value_lt' in data and 'value_gt' in data) and
               data['value_lt'] <= data['value_gt']
           ):
            raise ValidationError('value_lt must be greater than price_gt')

    country = ma.String(required=False,
                        validate=validate.Length(min=3, max=255))
    first_name = ma.String(required=False,
                           validate=validate.Length(min=3, max=255))
    last_name = ma.String(required=False,
                          validate=validate.Length(min=3, max=255))
    team_name = ma.String(required=False,
                          validate=validate.Length(min=3, max=255))
    price = ma.Integer(required=False,
                       validate=[validate.Range(min=0, min_inclusive=False,
                                                max=9223372036854775807,
                                                max_inclusive=True)])
    price_gt = ma.Integer(required=False,
                          validate=validate.Range(min=0, min_inclusive=True,
                                                  max=9223372036854775807,
                                                  max_inclusive=False))
    price_lt = ma.Integer(required=False,
                          validate=validate.Range(min=1, min_inclusive=False,
                                                  max=9223372036854775807,
                                                  max_inclusive=True))
    value = ma.Integer(required=False,
                       validate=[validate.Range(min=0, min_inclusive=False,
                                                max=9223372036854775807,
                                                max_inclusive=True)])
    value_gt = ma.Integer(required=False,
                          validate=validate.Range(min=0, min_inclusive=True,
                                                  max=9223372036854775807,
                                                  max_inclusive=False))
    value_lt = ma.Integer(required=False,
                          validate=validate.Range(min=1, min_inclusive=False,
                                                  max=9223372036854775807,
                                                  max_inclusive=True))
