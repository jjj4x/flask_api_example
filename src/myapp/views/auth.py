"""MYAPP authentication and authorization controllers."""
from datetime import datetime
from http import HTTPStatus

from flask import current_app
from flask_security.utils import verify_password
from flask_login import current_user

from myapp import (  # noqa: WPS347
    APIMethodView,
    APIBlueprint,
    APIError,
    JWT,
    anonymous_required,
    db,
    schemas,
    register_user,
    confirmation_token_link,
    confirmation_token_check,
    confirmation,
    parse,
    jwt_required,
    UserModel,
)

AUTH_BLUEPRINT = APIBlueprint('auth', __name__)


class LoginView(APIMethodView):
    """Login resource."""

    schema = schemas.LoginResponseSchema()

    @anonymous_required
    @parse(schemas.LoginRequestSchema(), location='json')
    def post(self, _, req):
        """
        JWT Authentication Endpoint.

        ---
        description: >
            # JWT Authentication Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: LoginRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: LoginResponseSchema
        """
        user = UserModel.query.filter_by(username=req['username']).one_or_none()

        if not (user and verify_password(req['password'], user.password)):
            raise APIError(
                'Bad Request: invalid credentials',
                metadata={'status': HTTPStatus.UNAUTHORIZED},
                http_status=HTTPStatus.UNAUTHORIZED,
            )

        access_token = JWT.encode(user)
        expires = datetime.utcnow() + current_app.config['JWT_EXPIRATION_DELTA']

        return self.schema, {
            'data': {'access_token': access_token, 'user': user},
            'metadata': {
                'cookies': [
                    {
                        'key': 'Authorization',
                        'value': f'{current_app.config["JWT_AUTH_HEADER_PREFIX"]} {access_token}',
                        'expires': expires,
                    },
                ],
            },
        }


class LogoutView(APIMethodView):
    """Logout resource."""

    schema = schemas.LogoutResponseSchema()

    @jwt_required
    @parse(schemas.LogoutRequestSchema(), location='json')
    def post(self, _, req):
        """
        JWT Authentication Endpoint.

        ---
        description: >
            # JWT Authentication Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: LogoutRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: LogoutResponseSchema
        """
        _ = req
        # NOTE: JWT is stateless and has no server-side logout capabilities.
        # https://stackoverflow.com/questions/37959945/how-to-destroy-jwt-tokens-on-logout#:~:text=You%20cannot%20manually%20expire%20a,DB%20query%20on%20every%20request.

        # We can use JWT token blacklist in Redis or something similar to
        # prohibit the access_token.

        return self.schema, {'data': {}}


class RegisterView(APIMethodView):
    """Register resource."""

    schema = schemas.RegisterResponseSchema()

    @anonymous_required
    @parse(schemas.RegisterRequestSchema(), location='json')
    def post(self, _, req):
        """
        Register new user view.

        ---
        description: >
            # Registration endpoint Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: RegisterRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: RegisterResponseSchema
        """
        res = {'data': {}}

        user = register_user(req)

        if current_app.config['SECURITY_CONFIRMABLE']:
            token_link = confirmation_token_link(user)

            if current_app.debug or current_app.testing:
                res['data']['confirmation_token_link'] = token_link

        res['data']['user'] = user

        db.session.add(user)
        db.session.commit()

        return self.schema, res


class ConfirmationTokenView(APIMethodView):
    """Confirmation Token resource."""

    schema = schemas.ConfirmationTokenResponseSchema()

    @anonymous_required
    @parse(schemas.ConfirmationTokenRequestSchema(), location='json')
    def get(self, _, r):
        """
        Generate or update confirmation token.

        ---
        description: >
            # Registration endpoint Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: ConfirmationTokenRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: ConfirmationTokenResponseSchema
        """
        res = {'data': {}, 'metadata': {}}

        if not current_app.config['SECURITY_CONFIRMABLE']:
            return self.schema, res

        res['metadata']['status'] = 5  # not found
        user = UserModel.query.filter_by(**r).one()

        already_confirmed = user.confirmed_at is not None
        if already_confirmed:
            raise APIError('Already confirmed', metadata={'status': 10})

        token_link = confirmation_token_link(user)

        if current_app.debug or current_app.testing:
            res['data']['confirmation_token_link'] = token_link

        res['metadata']['status'] = 0
        return self.schema, res


class ConfirmView(APIMethodView):
    """Confirmation resource."""

    schema = schemas.ConfirmResponseSchema()

    @anonymous_required
    @parse(schemas.ConfirmRequestSchema(), location='query')
    def get(self, _, r):
        """
        Confirm new user view.

        ---
        description: >
            # Registration endpoint Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: ConfirmRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: ConfirmResponseSchema
        """
        expired, invalid, user = confirmation_token_check(**r)
        already_confirmed = user.confirmed_at is not None

        if expired:
            raise APIError('Confirmation expired', metadata={'status': 9})

        if already_confirmed:
            raise APIError(
                'Already confirmed',
                schema=self.schema,
                data={'user': user},
                metadata={'status': 10},
            )

        user = confirmation(user)
        db.session.add(user)
        db.session.commit()

        return self.schema, {'data': {'user': user}}


class ChangePasswordView(APIMethodView):
    """Change password resource."""

    schema = schemas.ChangePasswordResponseSchema()

    @parse(schemas.ChangePasswordRequestSchema(), location='json')
    def post(self, _, req):
        """
        Change user's password.

        ---
        description: >
            # Registration endpoint Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: ChangePasswordRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: ChangePasswordResponseSchema
        """
        is_anonymous = False
        try:
            JWT.from_headers()
        except APIError:
            is_anonymous = True

        if is_anonymous:
            if not req['token']:
                raise APIError('Cannot reset password', metadata={'status': 9})

            expired, invalid, user = confirmation_token_check(req['token'])
            already_confirmed = user.confirmed_at is not None

            if expired:
                raise APIError('Confirmation expired', metadata={'status': 9})

            if not already_confirmed:
                user = confirmation(user)

        else:
            user = current_user

        if not verify_password(req['old_password'], user.password):
            raise APIError('Password does not match', metadata={'status': 9})

        user.set_password(req['new_password'])

        db.session.add(user)
        db.session.commit()

        return self.schema, {'data': {'user': user}}


class RestorePasswordView(APIMethodView):
    """Restore password resource."""

    schema = schemas.RestorePasswordResponseSchema()

    @parse(schemas.RestorePasswordRequestSchema(), location='json')
    def post(self, _, r):
        """
        Confirm new user view.

        ---
        description: >
            # Registration endpoint Endpoint.
        parameters:
            -
                in: query
                schema: APICommonRequestSchema
            -
                in: query
                schema: RestorePasswordRequestSchema
        responses:
            200:
                description: Describing the response
                content:
                    application/json:
                        schema: RestorePasswordResponseSchema
        """
        res = {'data': {}}

        user = UserModel.query.filter_by(email=r['email']).one_or_none()
        if user is None:
            raise APIError('Go away', metadata={'status': 9})

        token_link = confirmation_token_link(user, endpoint='auth.change_password')
        if current_app.debug or current_app.testing:
            res['data']['confirmation_token_link'] = token_link

        return self.schema, res
