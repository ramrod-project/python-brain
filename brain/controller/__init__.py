"""
manipulate the controller database
"""

NAME_KEY = "Name"
ID_KEY = "id"
SERVICE_KEY = "ServiceName"
PLUGIN_STATE_KEY = "PluginState"
UDP_KEY = "UDPPorts"
TCP_KEY = "TCPPorts"
TCP_STR = "tcp"
UDP_STR = "udp"

CONFLICT_ACTION = "update"

AVAILABLE = "Available"
ACTIVE = "Active"
STOPPED = "Stopped"
RESTARTING = "Restarting"


DESIRE_ACTIVE = "Activate"
DESIRE_RESTART = "Restart"
DESIRE_STOP = "Stop"
DESIRE_NONE = ""

ADDRESS_KEY = "Interface"
DESIRED_STATE_KEY = "DesiredState"

EX_PORTS_KEY = "ExternalPorts"
IN_PORTS_KEY = "InternalPorts"
ENV_KEY = "Environment"

PORT_SEPARATOR = "/"
ENV_SEPARATOR = "="

ALLOWED_PROTOCOLS = frozenset((TCP_STR, UDP_STR))

ALLOWED_DESIRED_STATES = frozenset((DESIRE_ACTIVE,
                                    DESIRE_RESTART,
                                    DESIRE_STOP,
                                    DESIRE_NONE))


ALLOWED_STATES = frozenset((ACTIVE,
                            AVAILABLE,
                            STOPPED,
                            RESTARTING))

ERRORS_KEY = "errors"
FIRST_ERROR = "first_error"
CONFLICT_ERROR_STRING = "{} conflicts(s): {} in use on {}"
UNKNOWN_PLUGIN_STRING = "Cannot update non-existent plugin!"
DUPLICATE_SERVICE_STRING = "Duplicate service name exists {}"
MOCK_ERROR_DICT = {ERRORS_KEY: 1,
                   FIRST_ERROR: ""}

from . import plugins
from . import interfaces