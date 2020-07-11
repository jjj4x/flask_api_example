from json import (
    JSONDecoder,
    JSONEncoder,
    loads as _json_loads,
)
from logging import getLogger
from pathlib import PosixPath

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Blueprint, current_app
from flask.views import MethodView
from webargs.flaskparser import FlaskParser
from marshmallow import Schema, fields, pre_dump, RAISE
from yaml import load, FullLoader


__all__ = [
    'APIMethodView',
    'APIBlueprint',
    'APIError',
    'APIRequestSchema',
    'APIResponseSchema',
    'APIMetadataSchema',
    'JSONEncoder',
    'JSONDecoder',
    'json_dump',
    'json_dumps',
    'json_loads',
    'parse',
    'OPEN_API',
]

log = getLogger(__name__)


class APIMethodView(MethodView):
    """API Method View."""


class APIBlueprint(Blueprint):
    """API Blueprint"""


class APIRequestParser(FlaskParser):
    def parse(
        self,
        argmap,
        req=None,
        *,
        location=None,
        validate=None,
        error_status_code=None,
        error_headers=None
    ):
        data = super().parse(
            argmap,
            req,
            location=location,
            validate=validate,
            error_status_code=error_status_code,
            error_headers=error_headers,
        )
        # log_request(req, data)
        return data

    def handle_error(self, error, req, schema, *, error_status_code, error_headers):
        raise APIError(
            'Failed on request parsing',
            metadata={'errors': error.messages},
        )

    def parse_files(self, req, name, field):
        raise NotImplementedError


parser = APIRequestParser()
parse = parser.use_args


class APIJSONEncoder(JSONEncoder):
    """MYAPP JSON Encoder."""

    def __init__(
        self,
        *,
        skipkeys=False,
        check_circular=True,
        allow_nan=True,
        separators=None,
        default=None,
    ):
        """Initialize encoder."""
        ensure_ascii = current_app.config['JSON_ENSURE_ASCII']
        sort_keys = current_app.config['JSON_SORT_KEYS']
        indent = current_app.config['JSON_INDENT']

        super().__init__(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
            default=default,
        )


class APIJSONDecoder(JSONDecoder):
    """MYAPP JSON Decoder."""

    def __init__(
        self,
        *,
        object_hook=None,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        strict=True,
        object_pairs_hook=None,
    ):
        """Initialize decoder."""
        super().__init__(
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            strict=strict,
            object_pairs_hook=object_pairs_hook,
        )


def json_dumps(obj, **kwargs):
    return APIJSONEncoder(**kwargs).encode(obj)


def json_dump(obj, file, **kwargs):
    for chunk in APIJSONEncoder(**kwargs).iterencode(obj):
        file.write(chunk)


def json_loads(string, **kwargs):
    return _json_loads(string, cls=APIJSONDecoder, **kwargs)


class APIError(Exception):
    """Base API Exception."""

    def __init__(self, *args, **kwargs):
        """Initialize API exception."""
        metadata = kwargs.pop('metadata', {})
        metadata.setdefault('message', "Error" if not args else args[0])
        metadata.setdefault('status', 3)
        self.json = APIResponseSchema().dump({'metadata': metadata})

        super().__init__(*args)


class APIRequestSchema(Schema):
    debug_tb_enabled = fields.Boolean(
        required=False,
        default=False,
    )

    class Meta:
        unknown = RAISE


class APIResponseSchema(Schema):
    data = fields.Dict(
        required=True,
        default=dict,
    )

    metadata = fields.Nested(
        'APIMetadataSchema',
        required=True,
    )

    @classmethod
    def default_metadata(cls):
        return {
            'status': 0,
            'message': 'Nice',
            'headers': {},
            'errors': None,
            'details': None,
        }

    @pre_dump
    def pre_dump(self, response, many=None):
        _ = many
        metadata = self.default_metadata()

        response_metadata = response.get('metadata', {})
        for field in 'status', 'message', 'headers', 'errors', 'details':
            if field in response_metadata:
                metadata[field] = response_metadata[field]

        # FIXME: dynamic messages
        if metadata['status'] and metadata['message'] == 'Nice':
            metadata['message'] = 'Not nice'

        response['metadata'] = metadata
        return response


class APIMetadataSchema(Schema):
    status = fields.Integer(
        required=True,
        default=0,
    )
    message = fields.String(
        required=True,
        default='Nice',
    )
    headers = fields.Dict(
        required=True,
        default=dict,
    )
    errors = fields.Dict(
        required=True,
        allow_none=True,
        default=None,
    )
    details = fields.Dict(
        required=True,
        allow_none=True,
        default=None,
    )


file_spec = {}
if not file_spec:
    with (PosixPath(__file__).parent / 'openapi.yml').open(encoding='utf8') as fd:
        file_spec = load(fd, Loader=FullLoader)

openapi_marshmallow_plugin = MarshmallowPlugin()
openapi_flask_plugin = FlaskPlugin()

OPEN_API = APISpec(
    file_spec["info"].pop("title"),
    file_spec["info"].pop("version"),
    file_spec.pop("openapi"),
    plugins=[
        openapi_flask_plugin,
        openapi_marshmallow_plugin,
    ],
    **file_spec,
)

# OPEN_API.components.schema('APIRequestSchema', schema=APIRequestSchema)
# OPEN_API.components.schema('APIResponseSchema', schema=APIResponseSchema)
# OPEN_API.components.schema('APIMetadataSchema', schema=APIMetadataSchema)
