from dataclasses import dataclass, field
from os import environ
from sys import stderr
from pathlib import PosixPath
from importlib import import_module
from inspect import getmembers, isclass
from uuid import uuid4
from logging import Filter

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema
from click import command, option
from flask import cli, current_app, has_request_context, request
from yaml import FullLoader, load as yaml_load


__all__ = [
    'APIConfig',
    'open_api_dump',
    'open_api_check',
]


class OpenAPIMarshmallowPlugin(MarshmallowPlugin):
    """For future overrides."""


class OpenAPIFlaskPlugin(FlaskPlugin):
    """For future overrides."""


def open_api_create():
    from myapp import APP_PATH, APIMethodView

    with (APP_PATH / 'openapi.yml').open(encoding='utf8') as fd:
        options = yaml_load(fd, Loader=FullLoader)

    open_api = APISpec(
        title=options['info'].pop('title'),
        version=options['info'].pop('version'),
        openapi_version=options.pop('openapi'),
        plugins=[
            OpenAPIMarshmallowPlugin(),
            OpenAPIFlaskPlugin(),
        ],
        **options,
    )

    for name, obj in getmembers(import_module('myapp.schemas')):
        if (isclass(obj) and issubclass(obj, Schema)) or isinstance(obj, Schema):
            open_api.components.schema(obj.__name__, schema=obj)

    with current_app.test_request_context():
        for view_function in current_app.view_functions.values():
            if (
                getattr(view_function, 'view_class', False)
                and issubclass(view_function.view_class, APIMethodView)
            ):
                open_api.path(view=view_function)

    return open_api


@command(name='open-api-dump')
@option('--filename', help='filename', default='myapp_open_api.json')
@cli.with_appcontext
def open_api_dump(filename):  # noqa: WPS216
    """
    Flask CLI open-api-dump command.

    """
    from myapp import json_dump

    open_api = open_api_create()

    file = PosixPath(filename)
    if file.is_dir():
        file = file / 'myapp_open_api.json'

    if not file.name.endswith('.json'):
        file = file.with_name(file.name + '.json')

    with file.open(encoding='utf8', mode='w') as fd:
        json_dump(open_api.to_dict(), fd)

    pass


@command(name='open-api-check')
@option('--print', help='print into stderr', is_flag=True, default=False)
@cli.with_appcontext
def open_api_check(is_print):  # noqa: WPS216
    """
    Flask CLI open-api-check command.

    """
    from myapp import json_dumps

    # May raise an exception and exit with non-zero code
    open_api = open_api_create()

    if is_print:
        print(json_dumps(open_api.to_dict()), file=stderr)


@dataclass
class APIConfig:
    SECRET_KEY: str = field(
        default=environ.get('SECRET_KEY'),
    )

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG_TB_ENABLED: bool = field(default=True)

    TRACEBACK_ENABLED: bool = field(default=True)
    TRACEBACK_TAIL_LENGTH: int = field(default=15)
    JSON_ENSURE_ASCII: bool = field(default=False)
    JSON_SORT_KEYS: bool = field(default=True)
    JSON_INDENT: int = field(default=4)

    LOGGING: dict = field(default_factory=lambda: {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'root': {
                'format': 'MYAPP[{process}] [{levelname}] [{name}] [{connection_id}] {message}',
                'datefmt': '%Y-%m-%dT%H:%M:%S',  # noqa: WPS323
                'style': '{',
                'class': 'logging.Formatter',
            },
        },
        'filters': {
            'connection_id_filter': {
                '()': 'myapp.config.ConnectionIDLoggingFilter',
                'connection_id_header': 'X-Connection-ID',
                'is_generate_if_not_set': True,
            }
        },
        'handlers': {
            'stream': {
                'class': 'logging.StreamHandler',
                'formatter': 'root',
                'stream': 'ext://sys.stderr',
                'filters': ['connection_id_filter'],
            },
        },
        'root': {
            'handlers': ['stream'],
            'level': 'INFO',
        },
        'loggers': {
            'werkzeug': {
                'level': 'WARNING',
                'propagate': True,
            },
            'flask': {
                'level': 'WARNING',
                'propagate': True,
            },
            'psycopg2': {
                'level': 'WARNING',
                'propagate': True,
            },
            'marshmallow': {
                'level': 'WARNING',
                'propagate': True,
            },
        },
    })

    def __post_init__(self):
        if not self.SECRET_KEY:
            raise ValueError('Specify SECRET_KEY.')

    @classmethod
    def from_yaml(cls, conf_filename: str):
        """
        Create config from YAML file.

        :param conf_filename: path to config
        :return: Config instance
        """
        with open(conf_filename, 'r', encoding='utf8') as fd:
            return cls(**yaml_load(fd, Loader=FullLoader))


class ConnectionIDLoggingFilter(Filter):
    def __init__(
        self,
        connection_id_header='X-Connection-ID',
        is_generate_if_not_set=True,
    ):
        super().__init__()
        self.connection_id_header = connection_id_header
        self.is_generate_if_not_set = is_generate_if_not_set

    def filter(self, record):
        connection_id = None
        if has_request_context():
            connection_id = getattr(request, 'connection_id', None)
            if not connection_id:
                connection_id = request.headers.get(self.connection_id_header)

            if not connection_id and self.is_generate_if_not_set:
                connection_id = uuid4()

            request.connection_id = connection_id

        record.connection_id = str(connection_id or 'X')

        return True
