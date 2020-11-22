"""Stats schemas."""
from marshmallow import Schema, fields

from myapp import APIRequestSchema, APIResponseSchema


class StatsRequestSchema(APIRequestSchema):
    """Stats request."""

    kind = fields.String(
        required=True,
        description='What kind of stats do you want?',
    )


class StatsResponseSchema(APIResponseSchema):
    """Stats response."""

    data = fields.Nested('StatsDataSchema')


class StatsDataSchema(Schema):
    """Stats data."""

    cpu_load = fields.String(
        required=False,
        description='CPU load.',
    )
    memory_free = fields.DateTime(
        required=False,
        description='Free RAM amount.',
    )
