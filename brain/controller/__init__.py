"""
manipulate the controller database
"""

NAME_KEY = "Name"
ID_KEY = "id"
SERVICE_KEY = "ServiceName"
UDP_KEY = "UDPPorts"
TCP_KEY = "TCPPorts"

CONFLICT_ACTION = "update"

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

EX_PORTS_KEY = "ExternalPorts"
IN_PORTS_KEY = "InternalPorts"
ENV_KEY = "Environment"

PORT_SEPARATOR = "/"
ENV_SEPARATOR = "="

ALLOWED_PROTOCOLS = frozenset(("tcp", "udp"))

ALLOWED_DESIRED_STATES = frozenset((DESIRE_ACTIVE,
                                    DESIRE_RESTART,
                                    DESIRE_STOP,
                                    DESIRE_NONE))


ALLOWED_STATES = frozenset((ACTIVE,
                            AVAILABLE,
                            STOPPED,
                            RESTARTING))

from . import plugins
from . import interfaces