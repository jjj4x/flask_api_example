from logging import config, getLogger
from os import environ
from sys import exc_info
from traceback import format_exc
from pathlib import PosixPath

from flask import Flask, signals, request, Response
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from werkzeug import exceptions

from myapp import (
    APIError,
    APIResponseSchema,
    APIConfig,
    open_api_dump,
    JSONEncoder,
    JSONDecoder,
    json_dumps,
)

SRC_PATH = PosixPath(__file__).parent.parent

debug_toolbar = DebugToolbarExtension()
db = SQLAlchemy()
migrate = Migrate()
flask_marshmallow = Marshmallow()
# TODO: Flask Security
# TODO: Flask JWT
# TODO: APISpec

log = getLogger(__name__)


def log_request():
    msg = fr"curl -w '\n' -iX {request.method} '{request.url}' "
    msg += ''.join(f"-H '{h}:{v}' " for h, v in request.headers.items())
    if (
        request.method in ('POST', 'PUT', 'PATCH')
        and request.headers.get('Content-Type') == 'application/json'
    ):
        msg += f"-d '{request.data.decode('utf8')}'"
    log.info(msg)


def log_response(response: Response):
    if response.is_json:
        log.info(f'Response: {response.json}')
    return response


class API(Flask):

    def __init__(self, *args, **kwargs):
        conf_filename = environ.get('MYAPP_FLASK_CONF_YAML')
        if conf_filename:
            conf = APIConfig.from_yaml(conf_filename)
        else:
            conf = APIConfig()

        config.dictConfig(conf.LOGGING)

        super().__init__(*args, **kwargs)

        self.config.from_object(conf)
        self.tc: APIConfig = conf

    def _response(
        self,
        json=None,
        status=1,
        http_status=200,
    ):
        if not json:
            json = APIResponseSchema().dump({'metadata': {'status': status}})

        if json['metadata'].get('status') is None:
            json['metadata']['status'] = status

        if self.config['DEBUG_TB_ENABLED'] and request.args.get('debug_tb_enabled'):
            data = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>MYAPP</title>
                </head>
                <body>
                    <pre>{0}</pre>
                </body>
                </html>
            """.format(json_dumps(json))
            json['metadata']['headers']['Content-Type'] = 'text/html'
        else:
            data = json_dumps(json)
            json['metadata']['headers']['Content-Type'] = 'application/json'

        return self.response_class(
            data,
            status=http_status,
            headers=json['metadata']['headers'],
        )

    def _json_from_uncaught_exception(self, status):
        exc_type, exc_value, _ = exc_info()

        details = {
            'exception_type': exc_type.__name__,
            'exception_value': str(exc_value),
            'exception_traceback': '',
        }
        if self.config['TRACEBACK_ENABLED']:
            tb = format_exc() or ''
            tb_tail = tb.split('\n')[-self.config['TRACEBACK_TAIL_LENGTH']:]
            details['exception_traceback'] = '\n'.join(tb_tail)

        json = {'metadata': {'status': status, 'details': details}}

        return APIResponseSchema().dump(json)

    def make_response(self, rv):
        # Don't do anything in make_response; use finalize_request instead
        return rv

    def finalize_request(self, rv, from_error_handler=False):
        if not rv:
            raise ValueError('Response cannot be empty.')

        if isinstance(rv, self.response_class):
            return rv

        schema, json, *_ = rv

        if not isinstance(schema, APIResponseSchema):
            raise TypeError('The Schema should inherit from APISchema.')

        response = self._response(json=schema.dump(json))

        # noinspection PyBroadException
        try:
            response = self.process_response(response)
            signals.request_finished.send(self, response=response)
        except Exception:
            if not from_error_handler:
                raise
            self.logger.exception(
                "Request finalizing failed with an error while handling an error"
            )

        return response

    def handle_user_exception(self, e):
        log.exception('User error.')

        # Generic HTTP Exception
        if isinstance(e, exceptions.HTTPException):
            return self.handle_http_exception(e)

        # Custom API Exception
        if isinstance(e, APIError):
            return self._response(json=e.json)

        # Maybe, Third-Party Exception Handler
        handler = self._find_error_handler(e)
        if handler is not None:
            return handler(e)

        # Any Uncaught Exception Raised by API
        return self._response(
            json=self._json_from_uncaught_exception(status=1),
            http_status=exceptions.InternalServerError.code,
        )

    def handle_http_exception(self, e):
        return self._response(status=1, http_status=e.code)

    def handle_exception(self, e):
        log.exception('Unexpected error.')
        return self._response(
            json=self._json_from_uncaught_exception(status=2),
            http_status=exceptions.InternalServerError.code,
        )


def create_app():
    app = API('MYAPP')

    app.json_encoder = JSONEncoder
    app.json_decoder = JSONDecoder

    app.before_request(log_request)
    app.after_request(log_response)

    from myapp.views import (
        GUYS_BLUEPRINT,
        GuysView,
        STATS_BLUEPRINT,
        StatsView,
    )

    GUYS_BLUEPRINT.add_url_rule('/guys', view_func=GuysView.as_view('guys'))
    STATS_BLUEPRINT.add_url_rule('/stats', view_func=StatsView.as_view('stats'))

    app.register_blueprint(GUYS_BLUEPRINT, url_prefix='/api/v1')
    app.register_blueprint(STATS_BLUEPRINT, url_prefix='/api/v1')

    if app.config['DEBUG_TB_ENABLED']:
        debug_toolbar.init_app(app)

    migrate.init_app(app, db=db, directory=SRC_PATH / 'myapp' / 'migrations')
    flask_marshmallow.init_app(app)

    app.cli.add_command(open_api_dump)

    return app
