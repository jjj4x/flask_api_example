"""Authentication and Authorization Service."""
from datetime import datetime
from functools import wraps
from logging import getLogger
from http import HTTPStatus

# noinspection PyProtectedMember
from flask import current_app, request, url_for, _request_ctx_stack  # noqa: WPS450
from flask_login import current_user
from flask_security.utils import hash_data, verify_hash
from jwt import InvalidTokenError, decode as jwt_decode, encode as jwt_encode
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from myapp import APIError, UserModel

LOG = getLogger(__name__)

__all__ = [
    'JWT',
    'jwt_required',
    'anonymous_required',
    'register_user',
    'confirmation_token_link',
    'confirmation_token_check',
    'confirmation',
]

# TODO: Sessions?


class JWT:
    """
    Flask-JWT rework.

    More info: https://flask-jwt-extended.readthedocs.io/en/stable/
    """

    @classmethod
    def encode(cls, user):
        """
        Encode a JWT token based on user's payload.

        :param user: UserModel
        :return: JWT token
        """
        secret = current_app.config['SECRET_KEY']
        algorithm = current_app.config['JWT_ALGORITHM']
        required_claims = current_app.config['JWT_REQUIRED_CLAIMS']

        iat = datetime.utcnow()
        exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
        nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')

        payload = {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': user.username}

        missing_claims = list(set(required_claims) - set(payload.keys()))

        if missing_claims:
            raise APIError(
                f'Missing claims: {missing_claims}',
                metadata={'status': HTTPStatus.UNAUTHORIZED},
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        return jwt_encode(payload, secret, algorithm=algorithm, headers=None)

    @classmethod
    def decode(cls, token):
        """
        Decode a JWT token.

        :param token: JWT token.
        :return: decoded payload.
        """
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

    @classmethod
    def from_headers(cls, realm=None):
        """
        Do the actual work of verifying the JWT data in the current request.

        This is done automatically for you by `jwt_required()` but you could call it manually.
        Doing so would be useful in the context of optional JWT access in your APIs.

        :param realm: an optional realm
        """
        realm = realm or current_app.config['JWT_DEFAULT_REALM']

        auth_header_value = request.headers.get('Authorization', None)
        auth_header_prefix = current_app.config['JWT_AUTH_HEADER_PREFIX']

        if not auth_header_value:
            raise APIError(
                "Authorization Required: request doesn't contain access token.",
                metadata={
                    'status': HTTPStatus.UNAUTHORIZED,
                    'headers': {'WWW-Authenticate': f'JWT realm="{realm}"'},
                },
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        parts = auth_header_value.split()

        if parts[0].lower() != auth_header_prefix.lower():
            raise APIError(
                'Invalid JWT header: unsupported authorization type.',
                metadata={'status': HTTPStatus.UNAUTHORIZED},
                http_status=HTTPStatus.UNAUTHORIZED,
            )
        elif len(parts) == 1:
            raise APIError(
                'Invalid JWT header: token missing.',
                metadata={'status': HTTPStatus.UNAUTHORIZED},
                http_status=HTTPStatus.UNAUTHORIZED,
            )
        elif len(parts) > 2:
            raise APIError(
                'Invalid JWT header: token contains spaces.',
                metadata={'status': HTTPStatus.UNAUTHORIZED},
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        token = parts[1]

        if token is None:
            raise APIError(
                "Authorization Required: request doesn't contain access token.",
                metadata={
                    'status': HTTPStatus.UNAUTHORIZED,
                    'headers': {'WWW-Authenticate': f'JWT realm="{realm}"'},
                },
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        try:
            payload = cls.decode(token)
        except InvalidTokenError:
            LOG.exception('Invalid JWT token')
            raise APIError(
                'Invalid JWT token',
                metadata={'status': HTTPStatus.UNAUTHORIZED},
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        user = UserModel.query.filter_by(username=payload.get('identity')).one_or_none()
        _request_ctx_stack.top.user = user  # flask_login compatible

        if user is None:
            raise APIError(
                'Invalid JWT: user does not exist or the username has changed.',
                metadata={'status': HTTPStatus.UNAUTHORIZED},
                http_status=HTTPStatus.UNAUTHORIZED,
            )


def register_user(payload):
    """Register new user."""
    return UserModel.create_new_user(**payload)


def confirmation_token_link(user, endpoint='auth.confirm'):
    """
    Create a confirmation token link based on user's email.

    :param user: UserModel
    :param endpoint: endpoint name; for URL generation
    :return: confirmation token link
    """
    ser = URLSafeTimedSerializer(
        secret_key=current_app.config['SECRET_KEY'],
        salt=current_app.config['SECRET_SALT'].encode(),
    )
    token = ser.dumps([user.username, hash_data(user.email)])

    confirmation_link = url_for(endpoint, token=token, _external=True)

    # FIXME: maybe a real email
    # security._send_mail(
    #     'MYAPP Registration Confirm.',
    #     user.email,
    #     "welcome",
    #     user=user,  noqa: E800
    #     confirmation_link=confirmation_link,  noqa: E800
    # )  noqa: E800

    return confirmation_link  # noqa: WPS331


def confirmation_token_check(token):
    """
    Check a confirmation token.

    :param token: A Token based on email.
    :return: is expired, is invalid, UserModel
    """
    ser = URLSafeTimedSerializer(
        secret_key=current_app.config['SECRET_KEY'],
        salt=current_app.config['SECRET_SALT'].encode(),
    )
    user = None
    max_age = current_app.config['SECURITY_CONFIRM_WITHIN']
    expired = False
    invalid = False
    try:
        data = ser.loads(token, max_age=max_age)
    except SignatureExpired:
        _, data = ser.loads_unsafe(token)
        expired = True
    except (BadSignature, TypeError, ValueError):
        data = None
        invalid = True

    if data:
        user = UserModel.query.filter_by(username=data[0]).one_or_none()

    expired = expired and (user is not None)

    if not invalid and user:
        user_id, token_email_hash = data
        invalid = not verify_hash(token_email_hash, user.email)

    return expired, invalid, user


def confirmation(user):
    """
    Confirm a user.

    :param user: UserModel
    :return: UserModel
    """
    user.confirmed_at = datetime.utcnow()
    return user


def jwt_required(realm=None):
    """View decorator that requires a valid JWT token to be present in the request.

    :param realm: an optional realm
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            JWT.from_headers(realm)
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def anonymous_required(f):
    """Enforce anonymous authorization."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        """Enforce anonymous authorization."""
        if current_user.is_authenticated:
            raise APIError(
                'Bad request: anonymous required.',
                metadata={'status': HTTPStatus.BAD_REQUEST},
                http_status=HTTPStatus.BAD_REQUEST,
            )
        return f(*args, **kwargs)
    return wrapper
