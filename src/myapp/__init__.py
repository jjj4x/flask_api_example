# ------------------------------THE ORDER MATTERS!------------------------------
# The <config> shouldn't import other MYAPP modules at the top level.
# Any other module can import the <config>.
from myapp.config import *
# The <core> is the top level entry point for GENERIC logic and abstractions.
# The <core> can import the <config>.
# The <core> can't import any other MYAPP module at the top level.
from myapp.core import *
# The <app> sets up the Flask application. It can leverage <config> and <core>.
from myapp.app import *
# The <lib> contains less generic logic then the <core>.
from myapp.lib import *
# The <models> should be initialized before <schemas> and <views>.
from myapp.models import *
# The <schemas> should be initialized before <views>.
from myapp.schemas import *
# The <services> contain service object that can span multiple models.
from myapp.services import *
# THe <views> contain controller/orchestrator logic; there they should go last.
from myapp.views import *
