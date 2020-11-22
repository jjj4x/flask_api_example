"""Authentication and Authorization serializers."""
from marshmallow import Schema, fields

from myapp import APIRequestSchema, APIResponseSchema, flask_marshmallow

CONFIRMATION_TOKEN_MAX_LENGTH = 200


class UserSchema(flask_marshmallow.Schema):
    """UserModel schema."""

    class Meta:
        """Meta configuration."""

        model = 'UserModel'
        fields = [
            'username',
            'email',
            'active',
            'confirmed_at',
            'roles',
        ]


class LoginRequestSchema(APIRequestSchema):
    """Login request."""

    username = fields.String(
        required=True,
        description='User name.',
    )
    password = fields.String(
        required=True,
        description='Password.',
    )


class LoginResponseSchema(APIResponseSchema):
    """Login response."""

    data = fields.Nested('LoginDataSchema')


class LoginDataSchema(Schema):
    """Login response data (payload) schema."""

    access_token = fields.String(
        required=True,
        description='JWT access token.',
    )
    user = fields.Nested(
        'UserSchema',
        required=True,
        description='User info.',
    )


class LogoutRequestSchema(APIRequestSchema):
    """Logout request."""

    username = fields.String(
        required=True,
        description='User name.',
    )


class LogoutResponseSchema(APIResponseSchema):
    """Logout response is empty."""


class RegisterRequestSchema(APIRequestSchema):
    """User registration request."""

    username = fields.String(
        required=True,
        description='Username.',
    )
    email = fields.Email(
        required=True,
        descripition='User email.',
    )
    password = fields.String(
        required=True,
        description='User password.',
    )


class RegisterResponseSchema(APIResponseSchema):
    """User registration response."""

    data = fields.Nested('RegisterDataSchema')


class RegisterDataSchema(Schema):
    """User registration data (payload)."""

    user = fields.Nested(
        'UserSchema',
        required=True,
        description='User info.',
    )
    confirmation_token_link = fields.String(
        required=False,
        description='Confirmation token link.',
    )


class ConfirmationTokenRequestSchema(APIRequestSchema):
    """Confirmation token request."""

    email = fields.Email(
        required=True,
        descripition='User email. Used for validation.',
    )


class ConfirmationTokenResponseSchema(APIResponseSchema):
    """Confirmation token response."""

    data = fields.Nested('ConfirmationTokenDataSchema')


class ConfirmationTokenDataSchema(Schema):
    """Confirmation token data (payload)."""

    confirmation_token_link = fields.String(
        required=False,
        description='Confirmation token link.',
    )


class ConfirmRequestSchema(APIRequestSchema):
    """Confirmation request."""

    token = fields.String(
        required=True,
        description='Confirmation token.',
        minLength=2,
        maxLength=CONFIRMATION_TOKEN_MAX_LENGTH,
    )


class ConfirmResponseSchema(APIResponseSchema):
    """Confirmation response."""

    data = fields.Nested('ConfirmDataSchema')


class ConfirmDataSchema(Schema):
    """Confirmation data (payload)."""

    user = fields.Nested(
        'UserSchema',
        required=True,
        description='User info.',
    )


class ChangePasswordRequestSchema(APIRequestSchema):
    """Change password request."""

    new_password = fields.String(
        required=True,
        description='New password',
    )
    old_password = fields.String(
        required=True,
        description='Old password',
    )
    token = fields.String(
        required=False,
        description='Confirmation token.',
    )


class ChangePasswordResponseSchema(APIResponseSchema):
    """Change password response."""

    data = fields.Nested('ChangePasswordDataSchema')


class ChangePasswordDataSchema(Schema):
    """Change password data (payload)."""

    user = fields.Nested(
        'UserSchema',
        required=True,
        description='User info.',
    )


class RestorePasswordRequestSchema(APIRequestSchema):
    """Restore password request."""

    email = fields.Email(
        required=True,
        descripition='User email.',
    )


class RestorePasswordResponseSchema(APIResponseSchema):
    """Restore password response is empty."""
