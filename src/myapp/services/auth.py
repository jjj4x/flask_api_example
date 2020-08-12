from datetime import datetime
from functools import wraps
from logging import getLogger

# noinspection PyProtectedMember
from flask import current_app, request, _request_ctx_stack
from werkzeug.local import LocalProxy
from jwt import InvalidTokenError, decode as jwt_decode, encode as jwt_encode

from myapp import APIError

LOG = getLogger(__name__)

current_identity = LocalProxy(
    lambda: getattr(_request_ctx_stack.top, 'current_identity', None),
)

__all__ = [
    'JWT',
    'jwt_required',
    'current_identity',
]


class JWT:
    """https://flask-jwt-extended.readthedocs.io/en/stable/"""

    @classmethod
    def encode(cls, identity):
        secret = current_app.config['SECRET_KEY']
        algorithm = current_app.config['JWT_ALGORITHM']
        required_claims = current_app.config['JWT_REQUIRED_CLAIMS']

        iat = datetime.utcnow()
        exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
        nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
        identity = getattr(identity, 'id', None) or identity['id']

        payload = {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}

        missing_claims = list(set(required_claims) - set(payload.keys()))

        if missing_claims:
            raise APIError(
                f'Missing claims: {missing_claims}',
                metadata={'status': 401},
                http_status=401,
            )

        return jwt_encode(payload, secret, algorithm=algorithm, headers=None)

    @classmethod
    def decode(cls, token):
        secret = current_app.config['SECRET_KEY']
        algorithm = current_app.config['JWT_ALGORITHM']
        leeway = current_app.config['JWT_LEEWAY']

        verify_claims = current_app.config['JWT_VERIFY_CLAIMS']
        required_claims = current_app.config['JWT_REQUIRED_CLAIMS']

        options = {'verify_' + claim: True for claim in verify_claims}
        options.update({'require_' + claim: True for claim in required_claims})

        return jwt_decode(
            token,
            secret,
            options=options,
            algorithms=[algorithm],
            leeway=leeway,
        )

    # TODO: proper handling
    @classmethod
    def identity_handler(cls, payload):
        return payload.get('identity')

    @classmethod
    def from_headers(cls, realm=None):
        """Does the actual work of verifying the JWT data in the current request.
        This is done automatically for you by `jwt_required()` but you could call it manually.
        Doing so would be useful in the context of optional JWT access in your APIs.

        :param realm: an optional realm
        """
        realm = realm or current_app.config['JWT_DEFAULT_REALM']

        auth_header_value = request.headers.get('Authorization', None)
        auth_header_prefix = current_app.config['JWT_AUTH_HEADER_PREFIX']

        if not auth_header_value:
            raise APIError(
                "Authorization Required: request doesn't contain access token",
                metadata={
                    'status': 401,
                    'headers': {'WWW-Authenticate': f'JWT realm="{realm}"'}
                },
                http_status=401,
            )

        parts = auth_header_value.split()

        if parts[0].lower() != auth_header_prefix.lower():
            raise APIError(
                'Invalid JWT header: unsupported authorization type',
                metadata={'status': 401},
                http_status=401,
            )
        elif len(parts) == 1:
            raise APIError(
                'Invalid JWT header: token missing',
                metadata={'status': 401},
                http_status=401,
            )
        elif len(parts) > 2:
            raise APIError(
                'Invalid JWT header: token contains spaces',
                metadata={'status': 401},
                http_status=401,
            )

        token = parts[1]

        if token is None:
            raise APIError(
                "Authorization Required: request doesn't contain access token",
                metadata={
                    'status': 401,
                    'headers': {'WWW-Authenticate': f'JWT realm="{realm}"'}
                },
                http_status=401,
            )

        try:
            payload = cls.decode(token)
        except InvalidTokenError:
            LOG.exception('Invalid JWT token')
            raise APIError(
                'Invalid JWT token',
                metadata={'status': 401},
                http_status=401,
            )

        identity = cls.identity_handler(payload)
        _request_ctx_stack.top.current_identity = identity

        if identity is None:
            raise APIError(
                'Invalid JWT: user does not exist',
                metadata={'status': 401},
                http_status=401,
            )


def jwt_required(realm=None):
    """View decorator that requires a valid JWT token to be present in the request

    :param realm: an optional realm
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            JWT.from_headers(realm)
            return fn(*args, **kwargs)
        return decorator
    return wrapper
