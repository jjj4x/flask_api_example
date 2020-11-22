"""MYAPP serialization schemas."""
from .auth import (
    LoginRequestSchema,
    LoginResponseSchema,
    LogoutRequestSchema,
    LogoutResponseSchema,
    RegisterRequestSchema,
    RegisterResponseSchema,
    ConfirmRequestSchema,
    ConfirmResponseSchema,
    ConfirmationTokenRequestSchema,
    ConfirmationTokenResponseSchema,
    ChangePasswordRequestSchema,
    ChangePasswordResponseSchema,
    RestorePasswordRequestSchema,
    RestorePasswordResponseSchema,
)
from .guys import (
    GuysRequestSchema,
    GuysResponseSchema,
)
from .stats import (
    StatsRequestSchema,
    StatsResponseSchema,
)
