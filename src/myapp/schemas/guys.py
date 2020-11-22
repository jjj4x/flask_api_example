"""Guys schema."""
from marshmallow import Schema, fields

from myapp import APIRequestSchema, APIResponseSchema


class GuysRequestSchema(APIRequestSchema):
    """Guys request."""

    full_name = fields.String(
        required=True,
        description='A random guy full name.',
    )
    dob = fields.DateTime(
        required=True,
    )


class GuysResponseSchema(APIResponseSchema):
    """Guys response."""

    data = fields.Nested('GuysDataSchema')


class GuysDataSchema(Schema):
    """Guys data."""

    identity = fields.Integer()
    name = fields.String()
