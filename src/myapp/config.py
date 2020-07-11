from dataclasses import dataclass, field
from os import environ
from sys import stderr
from pathlib import PosixPath

from click import command, option, prompt, echo
from flask import cli, current_app
from flask_security import utils
from yaml import FullLoader, load as yaml_load


__all__ = [
    'APIConfig',
    'open_api_dump',
    'open_api_check',
]


def open_api_create():
    from myapp import OPEN_API, APIMethodView

    with current_app.test_request_context():
        for view_function in current_app.view_functions.values():
            if (
                getattr(view_function, 'view_class', False)
                and issubclass(view_function.view_class, APIMethodView)
            ):
                OPEN_API.path(view=view_function)


@command(name='open-api-dump')
@option('--filename', help='filename', default='myapp_open_api.json')
@cli.with_appcontext
def open_api_dump(filename):  # noqa: WPS216
    """
    Flask CLI open-api-dump command.

    """
    from myapp import OPEN_API, json_dump

    open_api_create()

    file = PosixPath(filename)
    if file.is_dir():
        file = file / 'myapp_open_api.json'

    if not file.name.endswith('.json'):
        file = file.with_name(file.name + '.json')

    with file.open(encoding='utf8', mode='w') as fd:
        json_dump(OPEN_API.to_dict(), fd)

    pass


@command(name='open-api-check')
@option('--print', help='print into stderr', is_flag=True, default=False)
@cli.with_appcontext
def open_api_check(is_print):  # noqa: WPS216
    """
    Flask CLI open-api-check command.

    """
    from myapp import OPEN_API, json_dumps

    # May throw
    open_api_create()

    if is_print:
        print(json_dumps(OPEN_API.to_dict()), file=stderr)


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
                'format': 'MYAPP[{process}] [{levelname}] [{name}] {message}',
                'datefmt': '%Y-%m-%dT%H:%M:%S',  # noqa: WPS323
                'style': '{',
                'class': 'logging.Formatter',
            },
        },
        'handlers': {
            'stream': {
                'class': 'logging.StreamHandler',
                'formatter': 'root',
                'stream': 'ext://sys.stderr',
            },
        },
        'root': {
            'handlers': ['stream'],
            'level': 'INFO',
        },
        'loggers': {
            'flask': {
                'level': 'DEBUG',
                'propagate': True,
            },
            'psycopg2': {
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
