from marshmallow import Schema, fields

from myapp import APIRequestSchema, APIResponseSchema


class AuthRequestSchema(APIRequestSchema):
    username = fields.String(
        required=True,
        description='User name.',
    )
    password = fields.String(
        required=True,
        description='Password.',
    )


class AuthDataSchema(Schema):
    access_token = fields.String(
        required=True,
        description='JWT access token.',
    )


class AuthResponseSchema(APIResponseSchema):
    data = fields.Nested(AuthDataSchema)
