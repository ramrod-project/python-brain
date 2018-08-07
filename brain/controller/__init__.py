"""
manipulate the controller database
"""

NAME_KEY = "Name"


AVAILABLE = "Available"
ACTIVE = "Active"
STOPPED = "Stopped"
RESTARTING = "Restarting"


DESIRE_ACTIVE = "Activate"
DESIRE_RESTART = "Restart"
DESIRE_STOP = "Stop"
DESIRE_NONE = ""

ADDRESS_KEY = "Address"
DESIRED_STATE_KEY = "DesiredState"

ALLOWED_DESIRED_STATES = frozenset((DESIRE_ACTIVE,
                                    DESIRE_RESTART,
                                    DESIRE_STOP,
                                    DESIRE_NONE))


ALLOWED_STATES = frozenset((ACTIVE,
                            AVAILABLE,
                            STOPPED,
                            RESTARTING))

from . import plugins
