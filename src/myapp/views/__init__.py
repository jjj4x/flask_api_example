"""MYAPP controllers."""
from .auth import (
    AUTH_BLUEPRINT,
    LoginView,
    LogoutView,
    ConfirmationTokenView,
    ConfirmView,
    RegisterView,
    ChangePasswordView,
    RestorePasswordView,
)
from .guys import (
    GUYS_BLUEPRINT,
    GuysView,
)
from .stats import (
    STATS_BLUEPRINT,
    StatsView,
)
