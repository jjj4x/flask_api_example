from marshmallow import Schema, fields

from myapp import APIRequestSchema, APIResponseSchema, OPEN_API


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


OPEN_API.components.schema('GuysBodySchema', schema=GuysBodySchema)
OPEN_API.components.schema('GuysRequestSchema', schema=GuysRequestSchema)
OPEN_API.components.schema('GuysResponseSchema', schema=GuysResponseSchema)
