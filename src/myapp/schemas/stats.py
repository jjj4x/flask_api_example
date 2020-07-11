from marshmallow import Schema, fields

from myapp import APIRequestSchema, APIResponseSchema, OPEN_API


class StatsRequestSchema(APIRequestSchema):
    kind = fields.String(
        required=True,
        description='What kind of stats do you want?',
    )


class StatsBodySchema(Schema):
    cpu_load = fields.String(
        required=False,
        description='CPU load.',
    )
    memory_free = fields.DateTime(
        required=False,
        description='Free RAM amount.',
    )


class StatsResponseSchema(APIResponseSchema):
    data = fields.Nested(StatsBodySchema)


OPEN_API.components.schema('StatsBodySchema', schema=StatsBodySchema)
OPEN_API.components.schema('StatsRequestSchema', schema=StatsRequestSchema)
OPEN_API.components.schema('StatsResponseSchema', schema=StatsResponseSchema)
