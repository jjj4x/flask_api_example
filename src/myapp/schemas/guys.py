from marshmallow import Schema, fields

from myapp import APIRequestSchema, APIResponseSchema


class GuysRequestSchema(APIRequestSchema):
    full_name = fields.String(
        required=True,
        description='A random guy full name.',
    )
    dob = fields.DateTime(
        required=True,
    )


class GuysBodySchema(Schema):
    identity = fields.Integer()
    name = fields.String()


class GuysResponseSchema(APIResponseSchema):
    data = fields.Nested(GuysBodySchema)
