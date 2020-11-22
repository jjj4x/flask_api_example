"""MYAPP Core application logic."""
from json import (
    JSONDecoder,
    JSONEncoder,
    loads as _json_loads,
)
from logging import getLogger
from pathlib import PosixPath
from http import HTTPStatus

from flask import Blueprint, current_app, request, Response
from flask.views import MethodView
from webargs.flaskparser import FlaskParser
from marshmallow import Schema, fields, pre_dump, RAISE, EXCLUDE

__all__ = [
    'APP_PATH',
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
    'log_request',
    'log_response',
]

LOG = getLogger(__name__)

# ----------------------------------CONSTANTS----------------------------------
APP_PATH = PosixPath(__file__).parent
# ----------------------------------CONSTANTS----------------------------------


# -------------------------------WEBARGS SETTINGS-------------------------------
class APIRequestParser(FlaskParser):
    def handle_error(self, error, req, schema, *, error_status_code, error_headers):
        raise APIError(
            'The request specification is invalid; check OpenAPI docs for more info.',
            metadata={'errors': error.messages},
            http_status=error_status_code or HTTPStatus.OK,
        )

    def parse_files(self, req, name, field):
        raise NotImplementedError


parser = APIRequestParser()
parse = parser.use_args
# -------------------------------WEBARGS SETTINGS-------------------------------


# --------------------------------SERIALIZATION--------------------------------
class APIRequestSchema(Schema):
    """MYAPP base request schema."""

    class Meta:
        """Raise on unknown parameters."""

        unknown = RAISE


class APICommonRequestSchema(Schema):
    """MYAPP common request parameters."""

    class Meta:
        """Do not react on unknown parameters."""

        unknown = EXCLUDE

    debug_tb_enabled = fields.Boolean(
        required=False,
        default=False,
    )


class APIResponseSchema(Schema):
    """MYAPP base response schema."""

    class Meta:
        """Exclude any unknown parameters."""

        unknown = EXCLUDE

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
        """
        Create default metadata.

        :return: metadata fallback
        """
        return {
            'status': 0,
            'message': 'Nice',
            'headers': {},
            'errors': None,
            'details': None,
        }

    @pre_dump
    def pre_dump(self, response, many=None):
        """
        Make pre dump handling.

        :param response: raw response
        :param many: is many
        :return: enriched raw response
        """
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
    """MYAPP Metadata schema."""

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
# --------------------------------SERIALIZATION--------------------------------


# ------------------------FLASK AND APPLICATION GENERICS------------------------
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
        """
        Initialize encoder.

        :param skipkeys: is skip
        :param check_circular: is check circular
        :param allow_nan: is allow nan
        :param separators: separator char
        :param default: default value
        """
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


def json_dumps(obj, **kwargs):
    """
    MYAPP json dumps.

    :param obj: object
    :param kwargs: any
    :return: json string
    """
    return APIJSONEncoder(**kwargs).encode(obj)


def json_dump(obj, file, **kwargs):
    """
    MYAPP json dump.

    :param obj: python object
    :param file: filename
    :param kwargs: any
    """
    for chunk in APIJSONEncoder(**kwargs).iterencode(obj):
        file.write(chunk)


def json_loads(string, **kwargs):
    """
    MYAPP json loads.

    :param string: json string
    :param kwargs: any
    :return: dict
    """
    return _json_loads(string, cls=APIJSONDecoder, **kwargs)


class APIMethodView(MethodView):
    """API Method View."""

    decorators = (
        parse(APICommonRequestSchema(), location='query'),
    )


class APIBlueprint(Blueprint):
    """API Blueprint."""


def log_request():
    """Log request in curl-based fashion."""
    msg = fr"curl -w '\n' -iX {request.method} '{request.url}' "
    msg += ''.join(f"-H '{h}:{v}' " for h, v in request.headers.items())
    if (
        request.method in {'POST', 'PUT', 'PATCH'}
        and request.headers.get('Content-Type') == 'application/json'
    ):
        msg += f"-d '{request.data.decode('utf8')}'"
    LOG.info(msg)


def log_response(response: Response):
    """
    Log response json.

    :param response: flask response
    :return: flask response
    """
    if response.is_json:
        LOG.info(f'Response: {response.json}')
    return response
# ------------------------FLASK AND APPLICATION GENERICS------------------------


# ---------------------------EXCEPTIONS AND MESSAGES---------------------------
class APIError(Exception):
    """Base API Exception."""

    def __init__(self, *args, **kwargs):
        """
        Initialize API exception.

        :param args: any
        :param kwargs: any
        """
        schema = kwargs.pop('schema', APIResponseSchema())
        data = kwargs.pop('data', {})
        metadata = kwargs.pop('metadata', {})
        metadata.setdefault('message', 'Error' if not args else args[0])
        metadata.setdefault('status', 3)
        self.json = schema.dump({'data': data, 'metadata': metadata})
        self.http_status = kwargs.pop('http_status', HTTPStatus.OK)

        super().__init__(*args)
# ---------------------------EXCEPTIONS AND MESSAGES---------------------------
